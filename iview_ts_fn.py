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

        # score値を描画する
        scrstr = '{:.4f}'.format(scores[n])
        
        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.8
        thickness = 2
        textsize, baseline = cv2.getTextSize(scrstr, fontFace, fontScale, thickness)

        image = cv2.putText(image, scrstr, (x + (w - textsize[0]) // 2, y + h//2), fontFace, fontScale, (0, 0, 255), thickness=thickness)
        

    alpha = 0.5
    image = (alpha * image.astype(float) + (1.0 - alpha) * mskim.astype(float)).astype(np.uint8)

    # windowsで実行する場合はこちら
    #plt.imshow(image)
    #plt.show()

    # yoods-dnnとWSLのUbuntuで実行する場合はこちら
    #サイズ変更
    SCALE = 0.5
    image_resize = cv2.resize(image, (int(cols*SCALE), int(rows*SCALE)))
    cv2.imshow("image", image_resize)

    #qが入力されるまで待つ
    k = cv2.waitKey(0)
    while k != ord("q"):
        k = cv2.waitKey(0)


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



def main(ts_filename, target, score_thr, **kwargs):
    model = torch.jit.load(ts_filename)

    # 推論対象のリストを作成
    if os.path.isfile(target):
        imfilenames = [ target ]
    elif os.path.isdir(target):
        imfilenames = glob.glob('{}/*'.format(target)) 
    else:
        raise RuntimeError('target dir or file ({}) not found'.format(target))

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

         #プロンプトにファイル名出力
        #base name
        print(str(os.path.basename(file)))
        #full path name
        print(str(file))   

        # 結果画像を作成
        show_result(image, size, pred_boxes, scores, pred_classes, pred_masks, score_thr)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='torch script化されたモデルを読み込んで推論を行います', add_help=True)
    parser.add_argument('ts_filename', help='torch scriptファイル名')
    parser.add_argument('--score_thr', help='スコアしきい値.この値よりも低い結果は表示されません.', default=0.7, type=float)
    parser.add_argument('--anno_file', help='アノテーションファイル名. 指定するとカテゴリ名が表示されます.')
    parser.add_argument('target', help='推論対象の画像or画像が格納されているディレクトリ名')
    args = parser.parse_args()

    main(**vars(args))
