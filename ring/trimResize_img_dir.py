#trim and resize org img(file or dir)

import os
import glob
import numpy as np
import cv2

TRIM_X = 460
TRIM_Y = 500
TRIM_W = 512
TRIM_H = 512
DST_W = 1024
DST_H = 1024

def main(org, dstDir):

     # 元画像のリストを作成
    if os.path.isfile(org):
        org_filename_list = [ org ]
    elif os.path.isdir(org):
        org_filename_list = glob.glob('{}/*'.format(org)) 
    else:
        raise RuntimeError('source dir or file ({}) not found'.format(org))

    #変換後ディレクトリ作成、既に存在した場合、エラー上げて終了
    os.makedirs(dstDir, exist_ok=False)

    for org_filename in org_filename_list:

        #dst_path
        dst_path = str(os.path.join(dstDir, os.path.basename(org_filename)))

        #org imgを読み取り
        org_img = cv2.imread(org_filename)

        #trim img
        trimmed_img = org_img[TRIM_Y:TRIM_Y+TRIM_H, TRIM_X:TRIM_X+TRIM_W]

        #resize img
        #default interpolation
        #resized_img = cv2.resize(trimmed_img, (int(1024), int(1024)))

        #INTER_CUBIC
        resized_img = cv2.resize(trimmed_img, dsize=(DST_W, DST_H), interpolation=cv2.INTER_CUBIC)

        cv2.imwrite(dst_path, resized_img)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='trim and resize org img(file or dir).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--org', help='org img file or dir', default='org_img', type=str)   
    parser.add_argument('--dstDir', help='dst img dir', default='TrimmedResized_img', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.org, args.dstDir)
    except Exception as e:
        print(e)