#At first convert Color bmp to gray scale.
#Then change rgb Depth bmp to gray scale and equalize histogram.
#Lastly merge depth gray and color gray scale to rgb jpg file.

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

    color_fname_list = [color_fname for color_fname in os.listdir(srcDir) if color_fname.startswith(COLOR_FILE_PREFIX)]

    for color_fname in color_fname_list:
       
        depth_fname = DEPTH_FILE_PREFIX + color_fname[len(COLOR_FILE_PREFIX):]

        #ディレクトリ名を追加
        depth_path = str(Path(srcDir).joinpath(depth_fname))
        color_path = str(Path(srcDir).joinpath(color_fname))
        
        check_path(depth_path)

        #color bmpファイルを読み取り
        color_img = cv2.imread(color_path)
       
        #カラーからgray scaleを取得
        gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)

        #depth bmpファイルをgray scaleとして読み取り
        depth_gray_img = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)

        #輝度平滑化
        equ_img = cv2.equalizeHist(depth_gray_img)

        # 高さ・幅を取得
        high, w = equ_img.shape
    
        # 入力画像と同じサイズで出力画像用の配列を生成(中身は空)
        dst_img = np.empty((high, w), dtype=np.uint8)
    
        for y in range(0, high):
            for x in range(0, w):
                # 黒：0以外は反転
                if equ_img[y][x] == 0 : dst_img[y][x] = equ_img[y][x]
                else: dst_img[y][x] = 255 - equ_img[y][x]

        #b:Depth g:gray r:gray
        rgb_img = merge(dst_img, gray_img, gray_img)

        #マージ後ファイルのパスを作成:bmpのまま
        dst_path = str(Path(dstDir).joinpath(MERGED_FILE_PREFIX + color_fname[len(COLOR_FILE_PREFIX):]))
          
        cv2.imwrite(dst_path, rgb_img)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='At first convert Color bmp to gray scale. Then change rgb Depth bmp to gray scale and equalize histogram. Lastly merge depth gray and color gray scale to rgb jpg file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--srcDir', help='directory of source depth & color bmp file', default='Color+Depth', type=str)   
    parser.add_argument('--dstDir', help='directory of destination rgb jpg file', default='MergedRGB', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.srcDir, args.dstDir)
    except Exception as e:
        print(e)