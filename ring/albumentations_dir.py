#augmentate by albumentation

import os
import glob
import numpy as np
import albumentations as A
import cv2
import json

TRANSFORM_TIMES = 10
IMG_DIR = "JPEGImages"
JSON_FILE_NAME = "annotations.json"
IMG_WIDTH = 1280
IMG_HIGHT = 1024

def main(orgDir, dstDir):
     # check org dir
    if not os.path.isdir(orgDir):
        raise RuntimeError('source dir ({}) does not exist'.format(orgDir))

    #make dst dir and sub img dir
    os.makedirs(dstDir, exist_ok=False)
    os.makedirs(str(os.path.join(dstDir, IMG_DIR)))

    json_file = str(os.path.join(orgDir, JSON_FILE_NAME))
    
    transform = A.Compose([
            A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=None, rotate_limit=45, p=1)], 
            bbox_params=A.BboxParams(format='coco'))
            
    org_json = json.load(open(json_file,'r'))
    
    dst_json = {}
    
    #transformed image id
    dst_img_id = 0
    
    #transformed polygon id
    dst_plg_id = 0
    
    for org_img in org_json["images"]:
        org_img_fname = org_img["file_name"]
        org_img_path = os.path.join(orgDir, org_img_fname)
        org_img_picture = cv2.imread(org_img_path, cv2.COLOR_BGR2RGB)
        org_img_id = org_img["id"]
        
        org_bboxes = []
        org_segs = []
        org_category_ids = []

        #get bboxs and segmentation with just now image_id
        for ann in org_json["annotations"]:
            if ann["image_id"] == org_img_id:
                org_bboxes.append(ann["bbox"] + ["ring"])
                org_segs.append(ann["segmentation"])
                
        #change segmentation to 2D points
        pts = np.array(org_segs, dtype=np.int32)
        pts = pts.reshape(-1, 2)
        
        #mask has the same shape to img but values are 0(black)
        zeros = np.zeros((org_img_picture.shape), dtype=np.uint8)
        mask = cv2.fillPoly(zeros, [pts], 1)
        
        #transform
        for i in range(TRANSFORM_TIMES):
            
            transformed = transform(
                image = org_img_picture,
                mask = mask,
                bboxes= org_bboxes
            )
        
            transformed_image = transformed["image"]
            transformed_mask = transformed["mask"]
            transformed_bboxes = transformed["bboxes"]
            
            transformed_area = cv2.CountNonZero(transformed_mask)
            
            #write img
            dst_img_fname = org_img_fname[:-4] + str(dst_img_id) + ".jpg"
            cv2.imwrite(str(os.path.join(dstDir, IMG_DIR, dst_img_fname)), transformed_image)
            
            #mask to segmentation
            image, contours, hierarchy = cv2.findContours(transformed_mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            dst_segs = []
            for contour in contours:
                contour = contour.flatten().tolist()
                # segmentation.append(contour)
                if len(contour) > 4:
                    dst_segs.append(contour)
                if len(dst_segs) == 0:
                    continue
                
            #append segmentation to new json
            for seg in dst_segs:
                dst_ann = []
                dst_ann["id"] = dst_plg_id
                dst_ann["image_id"] = dst_img_id
                dst_ann["category_id"] = 0 
                dst_ann["segmentation"] = seg
                dst_ann["area"] = transformed_area
                dst_ann["bbox"] = transformed_bboxes
                dst_ann["iscrowd"] = 0
                
                dst_json["annotations"].append(dst_ann)
                dst_plg_id += 1
                
                
            dst_img_id += 1
            
    dst_json["categories"] = [{"supercategory": "null", "id": 0, "name": "ring"}]
    
    #write json file
    with open(str(os.path.join(dstDir, JSON_FILE_NAME)), "w") as f:
        json.dump(dst_json, f)    
        
        
        
        


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='augmentate by albumentation(file or dir).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--orgDir', help='org json file dir', default='org_coco', type=str)   
    parser.add_argument('--dstDir', help='dst json file dir', default='augmentated', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.orgDir, args.dstDir)
    except Exception as e:
        print(e)