#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as pltcmap
import math

import cv2
import torch
import torchvision  # jit.loadを行うときにこれをimportしていないとnmsがないと言われて落ちる

from plyfile import PlyData, PlyElement

# read ply file 
def read_ply(src_ply_dir):
    plydata = PlyData.read(src_ply_dir)
    
    return plydata

# write ply file
def write_ply(dst_ply_path, plydata):
    PlyData(plydata).write(dst_ply_path)
    

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
    src_plydata = read_ply(src_ply_fpath)
    src_pc = src_plydata['vertex'].data
    
    dtype = [('x', 'f'), ('y', 'f'), ('z', 'f'), ('red', 'uint8'), ('green', 'uint8'), ('blue', 'uint8')]
    src_pc_array_x = np.array(src_plydata['vertex'].data["x"])
    src_pc_array_y = np.array(src_plydata['vertex'].data["y"])
    src_pc_array_z = np.array(src_plydata['vertex'].data["z"])
   
    src_pc_array_red = np.array(src_plydata['vertex'].data["red"])
    src_pc_array_green = np.array(src_plydata['vertex'].data["green"])
    src_pc_array_blue = np.array(src_plydata['vertex'].data["blue"])
    
   

    for n in reversed(range(len(scores))):
   
        if scores[n] < score_thr:
            continue
        
        mskim = np.zeros(image.shape, dtype=np.uint8)

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
        _, mask = cv2.threshold(mask, 128, 1, cv2.THRESH_BINARY)

        #msk_plydata = PlyData()

        sum_mask_points = np.sum(mask)
        
        msk_points = np.zeros(sum_mask_points, dtype=dtype)
        
        count_points = 0
        for i_w in range(w):
            for i_h in range(h):
                if mask[i_h, i_w] == 1:
                    position = (i_h + y) * 1280 + i_w + x
                    print("i_h:", i_h, " i_w:", i_w, " position:", position)
                    msk_points[count_points] = src_plydata['vertex'].data[position]
                    count_points +=1
                    
                    
        vertex = np.array(msk_points, dtype=dtype)
        el = PlyElement.describe(vertex, 'vertex')
        
        dst_ply_fn = ply_ftitle + "_" + "{0:02d}".format(n) + ".ply"
        dst_ply_fpath = str(os.path.join(dst_ply_dir, dst_ply_fn))

        PlyData([el], text=False).write(dst_ply_fpath)
    

def write_msk_img(src_fn, image, dstsize, pred_boxes, scores, pred_classes, pred_masks, score_thr):
    rows, cols = image.shape[:2]
    rate = cols / dstsize[0]

    cmap = pltcmap.get_cmap("tab20")

    #ファイル名を分解
    ftitle, fext = os.path.splitext(src_fn)

    for n in reversed(range(len(scores))):
        
        if scores[n] < score_thr:
            continue
        
        mskim = np.zeros(image.shape, dtype=np.uint8)

        col = cmap(n)[:3]
        color = (int(255.0 * col[0]), int(255.0 * col[1]), int(255.0 * col[2]))
         
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
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE, offset=(x, y))
        
        # 領域を塗りつぶす
        mskim = cv2.drawContours(mskim, contours, -1, tuple(color), thickness = -1)

        dst_fn = ftitle + '_' + '{0:02d}'.format(n) + fext

        cv2.imwrite(dst_fn, mskim)


def show_result(image, dstsize, pred_boxes, scores, pred_classes, pred_masks, score_thr):
    rows, cols = image.shape[:2]
    rate = cols / dstsize[0]

    mskim = np.zeros(image.shape, dtype=np.uint8)
    cmap = pltcmap.get_cmap("tab20")
    for n in reversed(range(len(scores))):
        if scores[n] < score_thr:
            continue
        
        col = cmap(n)[:3]
        color = (int(255.0 * col[0]), int(255.0 * col[1]), int(255.0 * col[2]))
         
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

        # アウトラインを描画
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE, offset=(x, y))
        image = cv2.drawContours(image, contours, -1, tuple(color), thickness = 2)

        # 領域を塗りつぶす
        mskim = cv2.drawContours(mskim, contours, -1, tuple(color), thickness = -1)


    alpha = 0.5
    image = (alpha * image.astype(float) + (1.0 - alpha) * mskim.astype(float)).astype(np.uint8)

    # windowsで実行する場合はこちら
    plt.imshow(image)
    plt.show()

    # yoods-dnnで実行する場合はこちら
    #cv2.imshow("image", image)
    #cv2.waitKey(0)


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



def main(output_type, ts_filename, target, score_thr, src_ply_dir, dst_ply_dir, **kwargs):
    model = torch.jit.load(ts_filename)

    # 推論対象のリストを作成
    if os.path.isfile(target):
        imfilenames = [ target ]
    elif os.path.isdir(target):
        imfilenames = glob.glob('{}/*'.format(target)) 
    else:
        raise RuntimeError('target dir or file ({}) not found'.format(target))

    # check & make dst ply dir
    os.makedirs(dst_ply_dir, exist_ok=False)

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

        

        if output_type == 1:
            #write mask ply file
            write_msk_ply(src_ply_dir, dst_ply_dir, file, image, size, pred_boxes, scores, pred_classes, pred_masks, score_thr)
        elif output_type == 2:
            #write mask image file
            write_msk_img(src_ply_dir, dst_ply_dir, file, image, size, pred_boxes, scores, pred_classes, pred_masks, score_thr)
        else:
            # 結果画像を作成
            show_result(image, size, pred_boxes, scores, pred_classes, pred_masks, score_thr)




if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='torch script化されたモデルを読み込んで推論を行います', add_help=True)
    parser.add_argument('ts_filename', help='torch scriptファイル名')
    parser.add_argument('--score_thr', help='スコアしきい値.この値よりも低い結果は表示されません.', default=0.7, type=float)
    parser.add_argument('--anno_file', help='アノテーションファイル名. 指定するとカテゴリ名が表示されます.')
    parser.add_argument('target', help='推論対象の画像or画像が格納されているディレクトリ名')
    parser.add_argument('--src_ply_dir', help="元のply file", default="exp_data/ply/src")
    parser.add_argument('--dst_ply_dir', help="mask ply fileの書込み先", default="exp_data/ply/dst")
    parser.add_argument("--output_type", help="出力がply file(1)かimg file(2)か画面に表示(3)", default=1, type=int)
    args = parser.parse_args()

    try:
        main(**(vars(args)))
    except Exception as e:
        print(e)