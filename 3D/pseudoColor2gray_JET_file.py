#change pseudo color image to gray depth image

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

def main(srcImg, dstImg):
    # bmpファイルをバイナリモードで読み込み
    color_img = cv2.imread(srcImg)
    
    cv2.imwrite(dstImg, Jet2Gray(color_img))
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='change false color image to gray depth image.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--srcImg', help='name of source false color bmp file', default='src.bmp', type=str)
    parser.add_argument('--dstImg', help='name of destination gray bmp file', default='dst.bmp', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.srcImg, args.dstImg)
    except Exception as e:
        print(e)