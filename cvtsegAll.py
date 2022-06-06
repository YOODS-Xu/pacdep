#元のjsonファイル名→orgに変換
#orgをrbox或いはbboxツールで変換

import os
import shutil
import cv2

from pathlib import Path

IMAGE_FILE_EXT = "JPG"
#JSON_FILE_EXT = "json"

def check_dir(input_dir):
    """ディレクトリの存在チェック
    Args:
        input_dir(string): 変換前カラー画像のディレクトリ

    Raises:
        OSError: 変換前ディレクトリが存在しない場合に生じます
    """
    # 変換前ディレクトリの存在をチェック
    dir_list = [ "train", "test" ]
    for dir_name in dir_list:
        path_name = Path(input_dir).joinpath(dir_name).joinpath("JPEGImages")

        if not path_name.exists():
            raise OSError(2, "No such directory", str(path_name))
        

    check_dir(input_dir)
    
    dir_list = [ "train", "test" ]    
    
    for dir_name in dir_list:
        input_path_name = Path(input_dir).joinpath(dir_name).joinpath("JPEGImages")
        output_path_name = Path(output_dir).joinpath(dir_name).joinpath("JPEGImages")
        
        #outputグレースケールファイルディレクトリ作成、既に存在した場合、エラー上げて終了
        Path(output_path_name).mkdir(parents=True, exist_ok=False)
        
        #ファイル一覧取得
        file_name_list = os.listdir(input_path_name)

        for f in file_name_list:
            img = cv2.imread(str(Path(input_path_name).joinpath(f)))
            
            #グレースケール変換
            if algorithm == "cvtcolor":
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                img_gray, _ =cv2.decolor(img)
                     
            cv2.imwrite(str(Path(output_path_name).joinpath(f)), img_gray)
            
        #Visualizationディレクトのコピー
        shutil.copytree(Path(input_dir).joinpath(dir_name).joinpath("Visualization"), Path(output_dir).joinpath(dir_name).joinpath("Visualization"))

        #annotations.jsonファイルのコピー
        shutil.copy(Path(input_dir).joinpath(dir_name).joinpath("annotations.json"), Path(output_dir).joinpath(dir_name).joinpath("annotations.json"))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert color images to gray scale.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input_dir', help='Directory of input color files', default='coco', type=str)
    parser.add_argument('--output_dir', help='Directory of output gray scale files', default='coco_gray', type=str)
    parser.add_argument('--decolor', dest='algorithm', action='store_const',
                        const='decolor', default='cvtcolor',
                        help='alogrithm for conversion:decolor')
    
    args = parser.parse_args()
    
    try:
        main(args.input_dir, args.output_dir, args.algorithm)
    except Exception as e:
        print(e)