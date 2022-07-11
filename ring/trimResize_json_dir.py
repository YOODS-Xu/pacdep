#trim and resize org img(file or dir)

import os
import glob
import numpy as np
import json

TRIM_X = 460
TRIM_Y = 500
TRIM_W = 512
TRIM_H = 512
DST_W = 1024
DST_H = 1024

def main(org, dstDir):

    # read json file name list
    if os.path.isfile(org):
        org_filename_list = [ org ]
    elif os.path.isdir(org):
        org_filename_list = glob.glob('{}/*'.format(org)) 
    else:
        raise RuntimeError('source dir or file ({}) not found'.format(org))

    # make dst dir
    os.makedirs(dstDir, exist_ok=False)

    for org_filename in org_filename_list:

        #dst_path
        dst_path = str(os.path.join(dstDir, os.path.basename(org_filename)))

        #read json
        with open(org_filename, "r") as org_json_file:
            org_json = json.load(org_json_file)

            
        #trim img & resize

        #resize rate
        rate_resize_W = DST_W / TRIM_W
        rate_resize_H = DST_H / TRIM_H

        i = 0
        for shape in org_json["shapes"]:
            shape_array = np.asarray(shape["points"])
            shape_array[:, 0]=  (shape_array[:, 0] - TRIM_X) * rate_resize_W
            shape_array[:, 1] =  (shape_array[:, 1] - TRIM_Y) * rate_resize_H
            
            org_json["shapes"][i]["points"] = shape_array.tolist()
            
            i += 1

        # update image size
        org_json["imageWidth"] = DST_W
        org_json["imageHeight"] = DST_H

        #write json
        with open(dst_path, "w") as dst_json_file:
            json.dump(org_json, dst_json_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='trim and resize org img(file or dir).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--org', help='org img file or dir', default='org_json', type=str)   
    parser.add_argument('--dstDir', help='dst img dir', default='TrimmedResized_json', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.org, args.dstDir)
    except Exception as e:
        print(e)