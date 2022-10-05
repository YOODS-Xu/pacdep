#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.log import WARN
import sys
# server debug
#sys.path.append("/home/pacdep/.venv/lib/python3.8/site-packages")

import os
import glob
from urllib.parse import MAX_CACHE_SIZE
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as pltcmap
import math

import cv2
import torch
import torchvision  # jit.loadを行うときにこれをimportしていないとnmsがないと言われて落ちる

from plyfile import PlyData, PlyElement

from logging import DEBUG, INFO, getLogger, StreamHandler, Formatter
logger = getLogger(__name__)
logger.setLevel(INFO)
ch = StreamHandler()
ch.setLevel(WARN)
formatter = Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s", datefmt='%Y/%m/%d %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)

WIDE_LENGTH = 1280

# write ply file
def write_msk_ply(src_ply_dir, dst_ply_dir, src_fn, image, dstsize, pred_boxes, scores, pred_classes, pred_masks, score_thr):
    
    rows, cols = image.shape[:2]
    rate = cols / dstsize[0]
    
    # base file name
    base_img_fn = os.path.basename(src_fn)
    img_ftitle, _ = os.path.splitext(base_img_fn)
    ply_ftitle = img_ftitle[:str.find(img_ftitle, "_")]
    src_ply_fn = ply_ftitle + ".ply"
    src_ply_fpath = str(os.path.join(src_ply_dir, src_ply_fn))
    
    # read ply file
    src_plydata = PlyData.read(src_ply_fpath)
    src_pc = src_plydata['vertex'].data
    
    dtype = [('x', 'f'), ('y', 'f'), ('z', 'f'), ('red', 'uint8'), ('green', 'uint8'), ('blue', 'uint8')]
    
    for n in reversed(range(len(scores))):
   
        if scores[n] < score_thr:
            continue
        
        #mskim = np.zeros(image.shape, dtype=np.uint8)

        # bounding box の開始点と終了点(但しfloat)
        x0, y0, x1, y1 = rate * pred_boxes[n]
        x = int(x0)             # 開始位置
        y = int(y0)
        w = math.ceil(x1 - x0)  # boxサイズ
        h = math.ceil(y1 - y0)

        # マスク画像(28x28)を画像に対応した大きさに拡大
        mask = cv2.resize(pred_masks[n].reshape(28, 28), (w, h))        
        mask = (mask * 255).astype(np.uint8)    # [0, 1]範囲から[0, 255]へ

        # しきい値処理
        _, mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)

        # アウトラインを取得
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 領域を1で塗りつぶす
        mask = cv2.drawContours(mask, contours, -1, 1, -1)

        # マスクの総point数
        sum_mask_points = np.sum(mask)
        
        msk_pc = np.zeros(sum_mask_points, dtype=dtype)
        
        count_points = 0
        for i_w in range(w):
            for i_h in range(h):
                # check if mask region
                if mask[i_h, i_w] == 1:
                    position = (i_h + y) * WIDE_LENGTH + i_w + x
                    
                    # check if not nan
                    not_nan = not np.isnan(src_plydata['vertex'].data[position]['x'])
                    if not_nan:
                        msk_pc[count_points] = src_plydata['vertex'].data[position]
                        count_points +=1
                    
        logger.info(f"get mask pc successfully  sum:{sum_mask_points}\tnot nan:{count_points}")
                    
        vertex = np.array(msk_pc, dtype=dtype)
        el = PlyElement.describe(vertex, 'vertex')
        
        dst_ply_fn = ply_ftitle + "_" + "{0:02d}".format(n) \
        + "_" + str(scores[n]) \
        + "_sum" + str(sum_mask_points) \
        + "_notNan" + str(count_points) + ".ply"
        
        dst_ply_fpath = str(os.path.join(dst_ply_dir, ply_subdirs[pred_classes[n]], dst_ply_fn))

        PlyData([el], text=False).write(dst_ply_fpath)


def adjust_size(orgsize, maximum_size = 1024):
    '''
    Mask-RCNNに渡す画像サイズを調整する.あまり大きすぎるとfeature mapが大きくなりすぎてGPUの
    メモリにのらないため.

    Returns
    -------
    (resizeimage_width, resizeimage_height)
    '''
    maximum = max(orgsize)
    if maximum < maximum_size:
        return orgsize

    rate = maximum_size / maximum
    return (int(rate * orgsize[1]), int(rate * orgsize[0]) )



def main(ts_filename, target, score_thr, src_ply_dir, dst_ply_dir, **kwargs):
    model = torch.jit.load(ts_filename)

    # 推論対象のリストを作成
    if os.path.isfile(target):
        imfilenames = [ target ]
    elif os.path.isdir(target):
        imfilenames = glob.glob('{}/*'.format(target)) 
    else:
        raise RuntimeError('target dir or file ({}) not found'.format(target))
    
    # check & make dst ply dir
    for i_dir in range(len(ply_subdirs)):
        os.makedirs(os.path.join(dst_ply_dir, ply_subdirs[i_dir]), exist_ok=False)
    

    # 一枚ずつ読み込み＆推論
    for file in imfilenames:
        # 画像読み込み
        image = cv2.imread(file, cv2.IMREAD_COLOR)

        # 調整されたサイズを取得
        size = adjust_size(image.shape[:2])

        # 入力画像の大きさを調整
        tmpim = cv2.resize(image, size)

        # 推論実行
        inputs = torch.as_tensor(tmpim.astype("float32").transpose(2, 0, 1))
        outputs = model(inputs)

        # 結果(CPUに持ってきてTensorからNumpy配列に変換)
        pred_boxes = outputs[0].detach().cpu().numpy()
        pred_classes = outputs[1].detach().cpu().numpy()                
        pred_masks = outputs[2].detach().cpu().numpy()
        scores = outputs[3].detach().cpu().numpy()
        
        #write mask ply file
        write_msk_ply(src_ply_dir, dst_ply_dir, file, image, size, pred_boxes, scores, pred_classes, pred_masks, score_thr)




if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='analyze scene ply to masks ply according masks from 2D pictures using torch script model', add_help=True)
    parser.add_argument('ts_filename', help='torch scriptファイル名')
    parser.add_argument('--score_thr', help='スコアしきい値.この値よりも低い結果は表示されません.', default=0.7, type=float)
    parser.add_argument('--anno_file', help='アノテーションファイル名. 指定するとカテゴリ名が表示されます.')
    parser.add_argument('target', help='推論対象の画像or画像が格納されているディレクトリ名')
    parser.add_argument('--src_ply_dir', help="元のply file", default="exp_data/ply/src")
    parser.add_argument('--dst_ply_dir', help="mask ply fileの書込み先", default="exp_data/ply/dst")
    
    args = parser.parse_args()
    
    # debug
    #args = parser.parse_args(['output_backup/output_22.07.14_yajima_ring_preExp_augmentation_added_inner_train1600_Anchor16_max300/model.ts', 'sample_data/yajima_ring/preExp/org/added_inner/org/test/JPEGImages'])

    try:
        # subdirs for ply: default order is ["surface", "backface"]
        # if diffrent order used in training model, the list should be changed !!!
        ply_subdirs = ["surface", "backface"]
        main(**(vars(args)))
    except Exception as e:
        print(e)