#Change rgb Depth bmp to H of Hsv.

import os
from pathlib import Path
#from telnetlib import GA
import numpy as np
import cv2


def check_path(input_path):
    """ディレクトリとファイルの存在チェック
    Args:
        input_path(string): ディレクトリまたはファイル

    Raises:
        OSError: 存在しない場合に生じます
    """

    path_name = Path(input_path)

    if not path_name.exists():
        raise OSError(2, "No such directory or file", str(path_name))


def rgb2CALrgb(src):
    # 高さ・幅・チャンネル数を取得
    high, w, c = src.shape
    
    # 入力画像と同じサイズで出力画像用の配列を生成(中身は空)
    dst = np.empty((high, w))
    intDst = np.empty((high, w), dtype=np.uint8)
    
    for y in range(0, high):
        for x in range(0, w):
            # R, G, Bの値を取得して0～1の範囲内にする
            [b, g, r] = src[y][x]

            # R, G, Bの値から計算
            intDst[y][x] = np.uint8(r * 0.59 + g * 0.3 + b * 0.11)
       
    return intDst


def merge(bArray, gArray, rArray):

    high, w = bArray.shape
    
    rgbArray = np.concatenate(\
        [bArray.reshape(high, w, 1), gArray.reshape(high, w, 1), rArray.reshape(high, w, 1)], \
            axis=2)
    
    return rgbArray



def main(srcDir, dstDir):

    #check 変換前画像ディレクトリ
    check_path(srcDir)

    #変換後ディレクトリ作成、既に存在した場合、エラー上げて終了
    Path(dstDir).mkdir(parents=True, exist_ok=False)

    depth_fname_list = [depth_fname for depth_fname in os.listdir(srcDir)]

    for depth_fname in depth_fname_list:

        #ディレクトリ名を追加
        depth_path = str(Path(srcDir).joinpath(depth_fname))
        
        check_path(depth_path)

        #depth bmpファイルを読み取り
        depth_color_img = cv2.imread(depth_path)
   
        #rgbから計算
        hsv_img = rgb2CALrgb(depth_color_img)
        
        dst_path = str(Path(dstDir).joinpath(depth_fname))
        cv2.imwrite(dst_path, hsv_img)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Change rgb Depth bmp to H of Hsv.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--srcDir', help='directory of source: depth color bmp file', default='depth_color', type=str)   
    parser.add_argument('--dstDir', help='directory of destination: depth gray scale file', default='depth_gray', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.srcDir, args.dstDir)
    except Exception as e:
        print(e)