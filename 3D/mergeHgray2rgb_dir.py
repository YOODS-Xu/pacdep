#At first change bgr Depth bmp to H of Hsv.
#Then convert Color bmp to gray scale.
#Lastly merge H and gray scale to bgr bmp file.

import os
from pathlib import Path
#from telnetlib import GA
import numpy as np
import cv2

COLOR_FILE_PREFIX = "Color"
DEPTH_FILE_PREFIX = "Depth"
MERGED_FILE_PREFIX = "Color"

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
dtype=np.uint8

def rgb2Hsv(src_img):
    # 高さ・幅・チャンネル数を取得
    high, w, c = src_img.shape
    
    # 入力画像と同じサイズで出力画像用の配列を生成(中身は空)
    intDst = np.empty((high, w), dtype=np.uint8)
    
    #bmpはBGRだが、RGB2HSVで正しい結果
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
       
    return intDst


def merge(bArray, gArray, rArray):

    high, w = bArray.shape
    
    bgrArray = np.concatenate(\
        [bArray.reshape(high, w, 1), gArray.reshape(high, w, 1), rArray.reshape(high, w, 1)], \
            axis=2)
    
    return bgrArray



def main(srcDir, dstDir):

    #check 変換前画像ディレクトリ
    check_path(srcDir)

    #変換後ディレクトリ作成、既に存在した場合、エラー上げて終了
    Path(dstDir).mkdir(parents=True, exist_ok=False)

    color_fname_list = [color_fname for color_fname in os.listdir(srcDir) if color_fname.startswith(COLOR_FILE_PREFIX)]

    for color_fname in color_fname_list:
       
        depth_fname = DEPTH_FILE_PREFIX + color_fname[len(COLOR_FILE_PREFIX):]

        #ディレクトリ名を追加
        depth_path = str(Path(srcDir).joinpath(depth_fname))
        color_path = str(Path(srcDir).joinpath(color_fname))
        
        check_path(depth_path)

        #depth bmpファイルを読み取り
        depth_color_img = cv2.imread(depth_path)

        #color bmpファイルを読み取り
        color_img = cv2.imread(color_path)
    
        #depthからHを取得
        hsv_img = rgb2Hsv(depth_color_img)
    
        #カラーからgray scaleを取得
        gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)

        #b:H g:gray r:gray
        bgr_img = merge(hsv_img, gray_img, gray_img)

        #b:g g:H r:gray
        #rgb_img = merge(gray_img, hsv_img, gray_img)

        #マージ後ファイルのパスを作成:bmpのまま
        dst_path = str(Path(dstDir).joinpath(MERGED_FILE_PREFIX + color_fname[len(COLOR_FILE_PREFIX):]))
          
        cv2.imwrite(dst_path, bgr_img)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='At first change bgr Depth bmp to H of Hsv. Then convert Color bmp to gray scale. Lastly merge H and gray scale to bgr bmp file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--srcDir', help='directory of source depth & color bmp file', default='Color+Depth', type=str)   
    parser.add_argument('--dstDir', help='directory of destination bgr bmp file', default='MergedBGR', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.srcDir, args.dstDir)
    except Exception as e:
        print(e)