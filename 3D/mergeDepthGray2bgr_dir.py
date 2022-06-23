#Merge depth and gray scale to bgr bmp file.

import os
from pathlib import Path
#from telnetlib import GA
import numpy as np
import cv2

DEPTH_FILE_PREFIX = "depth"
GRAY_FILE_PREFIX = "gray"
MERGED_FILE_PREFIX = "merged"

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
    
    bgrArray = np.concatenate(\
        [bArray.reshape(high, w, 1), gArray.reshape(high, w, 1), rArray.reshape(high, w, 1)], \
            axis=2)
    
    return bgrArray



def main(srcDir, dstDir, depthBGRtype):

    if depthBGRtype != "b" and depthBGRtype != "g" and depthBGRtype != "r" \
        and depthBGRtype != "bg" and depthBGRtype != "br" and depthBGRtype != "gr":

        print(depthBGRtype, " is not a correct depthBGRtype")
        print("depthBGRtype should be one of b, g, r, bg, br or gr")
        return

    #check 変換前画像ディレクトリ
    check_path(srcDir)

    #変換後ディレクトリ作成、既に存在した場合、エラー上げて終了
    Path(dstDir).mkdir(parents=True, exist_ok=False)

    gray_fname_list = [gray_fname for gray_fname in os.listdir(srcDir) if gray_fname.startswith(GRAY_FILE_PREFIX)]

    for gray_fname in gray_fname_list:
       
        depth_fname = DEPTH_FILE_PREFIX + gray_fname[len(GRAY_FILE_PREFIX):]

        #ディレクトリ名を追加してファイルパス
        depth_path = str(Path(srcDir).joinpath(depth_fname))
        gray_path = str(Path(srcDir).joinpath(gray_fname))
        
        check_path(depth_path)

        #depth bmpファイルを読み取り
        depth_img = cv2.imread(depth_path)
        #depth bmpはbgr同じのgray scale
        depth_array = cv2.split(depth_img)
        depth_r = depth_array[0]

        #gray bmpファイルを読み取り
        gray_img = cv2.imread(gray_path)
        #gray bmpはbgr同じのgray scale
        gray_array =  cv2.split(gray_img)
        gray_r = gray_array[0]
       
        if depthBGRtype == "b":
            #b:depth g:gray r:gray
            bgr_img = merge(depth_r, gray_r, gray_r)
        elif depthBGRtype == "g":
            #b:gray g:depth r:gray
            bgr_img = merge(gray_r, depth_r, gray_r)
        elif depthBGRtype == "r":
            #b:gray g:gray r:depth
            bgr_img = merge(gray_r, gray_r, depth_r)
        elif depthBGRtype == "bg":
            #b:depth g:depth r:gray
            bgr_img = merge(depth_r, depth_r, gray_r)
        elif depthBGRtype == "br":
            #b:depth g:gray r:depth
            bgr_img = merge(depth_r, gray_r, depth_r)
        elif depthBGRtype == "gr":
            #b:depth g:gray r:depth
            bgr_img = merge(gray_r, depth_r, depth_r)
        else:
            print(depthBGRtype, " is not a correct depthBGRtype")
            print("depthBGRtype should be one of b, g, r, bg, br or gr")
            return

        #マージ後ファイルのパスを作成:bmpのまま
        dst_path = str(Path(dstDir).joinpath(MERGED_FILE_PREFIX + gray_fname[len(GRAY_FILE_PREFIX):]))
          
        cv2.imwrite(dst_path, bgr_img)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Merge depth and gray scale to bgr bmp file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--srcDir', help='directory of source depth & gray bmp file', default='Depth+Gray', type=str)   
    parser.add_argument('--dstDir', help='directory of destination bgr bmp file', default='MergedBGR', type=str)
    parser.add_argument('--depthBGRtype', help='use depth as b, g, r, bg, br or gr', default='b', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.srcDir, args.dstDir, args.depthBGRtype)
    except Exception as e:
        print(e)