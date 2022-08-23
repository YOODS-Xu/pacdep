#augmentate org img and json(polygon)
#check if out of bounds

from operator import truediv
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
    
    random.seed(316)

    # for all images
    for org_img_fname in org_img_fname_list:

        #read img
        org_img = cv2.imread(org_img_fname)

        #height, width of the img
        height, width, _  = org_img.shape

        #augmentate
        i = 1
        while i <= aug_num:

            # get random parameters
            #up and down
            ty = random.randint(TY_UP, TY_DOWN)

            #left and right
            tx = random.randint(TX_UP, TX_DOWN)

            #rotate
            t_r = random.uniform(TR_MIN, TR_MAX)

            #up down and left right transform
            M = np.float32([[1, 0, tx],[0, 1, ty]])

            # up down and left right image
            img_upD_leftR = cv2.warpAffine(org_img, M, (width, height))
            
            #rotate
            #center coor is (x, y)
            center = (int((width-1)/2), (int((height-1)/2)))
            
            M = cv2.getRotationMatrix2D(center, t_r, 1)
            
            # rotate image
            dst_img = cv2.warpAffine(img_upD_leftR, M, (width, height))
            
            # augmentate json
            #org json path
            org_json_path = str(os.path.splitext(org_img_fname)[0]) + JSON_EXT

            #read json
            with open(org_json_path, "r") as org_json_file:
                org_json = json.load(org_json_file) 

            #for all shapes
            j = 0
            in_bounds = True
            for shape in org_json["shapes"]:
                #if all shapes are in_bounds then augmentate
                if in_bounds:
                    shape_array = np.array(shape["points"])

                    #up down and left right transform
                    shape_array[:, 0] =  shape_array[:, 0] + tx
                    shape_array[:, 1] =  shape_array[:, 1] + ty
               
                    #rotate
                    #get coor from center
                    shape_array[:, 0] = shape_array[:, 0] - center[0]
                    shape_array[:, 1] = shape_array[:, 1] - center[1]
                
                    #turn clockwise to counterclockwise
                    new_M = np.flipud(np.fliplr(M[:, :2]))
                    new_shape_array = np.dot(shape_array, new_M)
                               
                    shape_array[:, 0] = new_shape_array[:, 0] + center[0]
                    shape_array[:, 1] = new_shape_array[:, 1] + center[1]
                
                    #check if out of bounds
                    x_min = min(shape_array[:, 0])
                    x_max = max(shape_array[:, 0])
                    y_min = min(shape_array[:, 1])
                    y_max = max(shape_array[:, 1])

                    if x_min < 0 or x_max > width or y_min < 0 or y_max > height:
                        in_bounds = False

                    #if not out of bounds
                    if in_bounds:
                        org_json["shapes"][j]["points"] = shape_array.tolist()

                #next shape
                j += 1

            #only not out of bounds can be written img and json file
            if in_bounds:
                #base file name
                dst_base_fname = str(os.path.splitext(os.path.basename(org_img_fname))[0]) + f"_{i:0{num_dig}}"

                #dst path of img
                dst_img_path = str(os.path.join(dstDir, (dst_base_fname + IMG_EXT)))

                #write img
                cv2.imwrite(dst_img_path, dst_img)

                # update img name
                org_json["imagePath"] = dst_base_fname + IMG_EXT

                #write json
                #dst path of json
                dst_json_path = str(os.path.join(dstDir, (dst_base_fname + JSON_EXT)))
                with open(dst_json_path, "w") as dst_json_file:
                    json.dump(org_json, dst_json_file)

                #next augmentate
                i += 1            


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='trim and resize org img(file or dir).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--orgDir', help='org img and json file dir', default='org_img_json', type=str)   
    parser.add_argument('--dstDir', help='dst dir', default='augmentated_img_json', type=str)
    parser.add_argument('--aug_num', help='number of augmentation', default='8', type=int)
    
    args = parser.parse_args()
    
    try:
        main(**(vars(args)))
    except Exception as e:
        print(e)