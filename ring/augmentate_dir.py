#augmentate org img and json(polygon)

import os
import glob
import numpy as np
import cv2
import json
import random

#need "."
IMG_EXT = ".bmp"
JSON_EXT = ".json"

TX_UP = -50
TX_DOWN = 50
TY_UP = -50
TY_DOWN = 50
TR_MIN = 0.0
TR_MAX = 180.0

def main(orgDir, dstDir, aug_num):

     # img fname list
    if os.path.isdir(orgDir):
        org_img_fname_list = glob.glob(f'{orgDir}/*{IMG_EXT}') 
    else:
        raise RuntimeError(f'source dir or file ({orgDir}) not found')

    # make dstDir
    os.makedirs(dstDir, exist_ok=False)

    # num of digits
    num_dig = len(str(aug_num))

    for i in range(aug_num):

        # get random parameters
        #up and down
        ty = random.randint(TY_UP, TY_DOWN)

        #left and right
        tx = random.randint(TX_UP, TX_DOWN)

        #rotate
        tr = random.uniform(TR_MIN, TR_MAX)

        #for all imgs
        for org_img_fname in org_img_fname_list:

            dst_base_fname = os.path.splitext(os.path.basename(org_img_fname))[0] + f"_{i:0>num_dig}"

            #augmentate img

            #dst path of img
            dst_img_path = str(os.path.join(dstDir, dst_base_fname, IMG_EXT))

            #read img
            org_img = cv2.imread(org_img_fname)

            #height, width of the img
            height, width = org_img.shape

            #up down and left right transform
            M = np.float32([[1, 0, tx],[0, 1, ty]])
            img_upD_leftR = cv2.warpAffine(org_img, M, (width, height))

            #rotate
            #center coor is (x, y)
            center = (int(width/2), (int(height/2)))

            M = cv2.getRotationMatrix2D(center, tr, 1.0)
            dst_img = cv2.warpAffine(img_upD_leftR, M, (width, height))

            #write img
            cv2.imwrite(dst_img_path, dst_img)


            # augmentate json

            #org json path
            org_json_path = str(os.path.splitext(os.path.basename(org_img_fname))[0]) + JSON_EXT

            #dst path of json
            dst_json_path = str(os.path.join(dstDir, dst_base_fname, JSON_EXT))


            #read json
            with open(org_filename, "r") as org_json_file:
            org_json = json.load(org_json_file)

            #INTER_CUBIC
            resized_img = cv2.resize(trimmed_img, dsize=(DST_W, DST_H), interpolation=cv2.INTER_CUBIC)

            


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='trim and resize org img(file or dir).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--orgDir', help='org img and json file dir', default='org_img_json', type=str)   
    parser.add_argument('--dstDir', help='dst dir', default='augmentated_img_json', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.org, args.dstDir)
    except Exception as e:
        print(e)