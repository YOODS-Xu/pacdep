#change pseudo color image to gray depth image by inverting COLORMAP_JET(cv2.applyColorMap)

import os
from pathlib import Path
import numpy as np
import cv2


def Jet2Gray(img):
    # create an inverse from the colormap to gray values
    gray_values = np.arange(256, dtype=np.uint8)
    color_values = map(tuple, cv2.applyColorMap(gray_values, cv2.COLORMAP_JET).reshape(256, 3))
    color_to_gray_map = dict(zip(color_values, gray_values))
    keys = list(color_to_gray_map.keys())
    
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            px = img[x, y]
            d_min = 100000
            best_val = px
            for key in keys:
                d = 0
                for i in range(3):
                    d += abs(float(px[i])-float(key[i]))
                if d < d_min:
                    best_val = np.array(key)
                    d_min = d
            img[x, y] = best_val

    # apply the inverse map to the pseudo color image to reconstruct the grayscale image
    gray_image = np.apply_along_axis(lambda bgr: color_to_gray_map[tuple(bgr)], 2, img)
    
    return gray_image



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

    for depth_fname in depth_fname_list:

        #ディレクトリ名を追加
        depth_path = str(Path(srcDir).joinpath(depth_fname))

        #depth bmpファイルを読み取り
        depth_pseudo_color_img = cv2.imread(depth_path)
   
        #change pseudo color image to gray scale image
        dst_img = Jet2Gray(depth_pseudo_color_img)
        
        dst_path = str(Path(dstDir).joinpath(depth_fname))
        cv2.imwrite(dst_path, dst_img)


    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='change pseudo color image to gray depth image by inverting COLORMAP_JET(cv2.applyColorMap).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--srcDir', help='directory of source: depth color bmp file', default='depth_color', type=str)   
    parser.add_argument('--dstDir', help='directory of destination: depth gray scale file', default='depth_gray', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.srcDir, args.dstDir)
    except Exception as e:
        print(e)