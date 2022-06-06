#Change rgb Depth bmp to H of Hsv.
#

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


def rgb2Hsv(src_img):
    # 高さ・幅・チャンネル数を取得
    high, w, c = src_img.shape
    
    # 入力画像と同じサイズで出力画像用の配列を生成(中身は空)
    intDst = np.empty((high, w), dtype=np.uint8)
    
    hsv_img = cv2.cvtColor(src_img, cv2.COLOR_RGB2HSV)
    h_img, s_img, v_img = cv2.split(hsv_img)
    
    minH = 255
    maxH = 0
    for y in range(0, high):
        for x in range(0, w):
            if h_img[y][x] != 0:
                if minH > h_img[y][x]: minH = h_img[y][x]
                if maxH < h_img[y][x]: maxH = h_img[y][x]
    
    f_ratio = 255.0/(maxH - minH)

    for y in range(0, high):
        for x in range(0, w):
            if h_img[y][x] != 0:
                intDst[y][x] = np.uint8((h_img[y][x] - minH)* f_ratio)
            else:
                intDst[y][x] = 0
       
    print("maxH:", maxH, " minH:",minH)
    return intDst


def main(srcDir, dstDir):

    #check 変換前画像ディレクトリ
    check_path(srcDir)

    #変換後ディレクトリ作成、既に存在した場合、エラー上げて終了
    Path(dstDir).mkdir(parents=True, exist_ok=False)

    depth_fname_list = [depth_fname for depth_fname in os.listdir(srcDir)]

    for depth_fname in depth_fname_list:

        #ディレクトリ名を追加
        depth_path = str(Path(srcDir).joinpath(depth_fname))

        #depth bmpファイルを読み取り
        depth_color_img = cv2.imread(depth_path)
   
        #depthからHを取得
        h_img = rgb2Hsv(depth_color_img)
        
        dst_path = str(Path(dstDir).joinpath(depth_fname))
        cv2.imwrite(dst_path, h_img)



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