#Contrast Limited Adaptive Histogram Equalization.

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


def main(srcDir, dstDir):

    #check 変換前画像ディレクトリ
    check_path(srcDir)

    #変換後ディレクトリ作成、既に存在した場合、エラー上げて終了
    Path(dstDir).mkdir(parents=True, exist_ok=False)

    depth_fname_list = [depth_fname for depth_fname in os.listdir(srcDir)]

    # create a CLAHE object (Arguments are optional).
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    

    for depth_fname in depth_fname_list:

        #ディレクトリ名を追加
        depth_path = str(Path(srcDir).joinpath(depth_fname))
        
        check_path(depth_path)

        #depth bmpファイルを読み取り
        depth_gray_img = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)
   
        #輝度平滑化
        ecl_img = clahe.apply(depth_gray_img)

        # 高さ・幅を取得
        high, w = ecl_img.shape
    
        # 入力画像と同じサイズで出力画像用の配列を生成(中身は空)
        dst_img = np.empty((high, w), dtype=np.uint8)
    
        for y in range(0, high):
            for x in range(0, w):
                # 黒：0以外は反転
                if ecl_img[y][x] == 0 : dst_img[y][x] = ecl_img[y][x]
                else: dst_img[y][x] = 255 - ecl_img[y][x]
        
        dst_path = str(Path(dstDir).joinpath(depth_fname))
        cv2.imwrite(dst_path, dst_img)


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