#カラー画像をグレースケール化:単独ディレクトの子ディレクトリの全部
#コマンドラインで指定↓
#カラーファイルディレクトリ:input_dir(デフォルト:color)
#グレースケールファイルディレクトリ:output_dir(デフォルト：gray)
#アルゴリズム：cvtcolor(作りこみ)

import os
import shutil
import cv2
from pathlib import Path
from glob import glob



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
    
    
        
def main(input_dir, output_dir):
    """変換メイン
    Args:
        input_dir(string): 変換前カラー画像のディフォルト
        output_dir(string): 変換後グレースケール画像のディフォルト
 
    Raises:
        FileExistsError: 出力先ディレクトリが既に存在した場合に生じます
    """
    
    #inputカラー画像ディフォルトの存在チェック
    check_dir(input_dir)
    
    subdir_list = [dir_name for dir_name in os.listdir(input_dir) if os.path.isdir(Path(input_dir).joinpath(dir_name))]
    
    for dir_name in subdir_list:
        input_path_name = Path(input_dir).joinpath(dir_name)
        output_path_name = Path(output_dir).joinpath(dir_name)
        
        #outputグレースケールファイルディレクトリ作成、既に存在した場合、エラー上げて終了
        Path(output_path_name).mkdir(parents=True, exist_ok=False)
        
        #ファイル一覧取得
        file_name_list = [f for f in os.listdir(input_path_name) if f.endswith(IMAGE_FILE_EXT)]

        for f in file_name_list:
            img = cv2.imread(str(Path(input_path_name).joinpath(f)))
            
            #グレースケール変換
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                      
            cv2.imwrite(str(Path(output_path_name).joinpath(f)), img_gray)
            
            #jsonファイルをコピー
            json_file_name = str(Path(f).stem) + "." + JSON_FILE_EXT
            shutil.copyfile(input_path_name.joinpath(json_file_name), output_path_name.joinpath(json_file_name))
            



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert color images in all subdir to gray scale.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input_dir', help='Directory of input color files', default='color', type=str)
    parser.add_argument('--output_dir', help='Directory of output gray scale files', default='gray', type=str)
        
    args = parser.parse_args()
    
    try:
        main(args.input_dir, args.output_dir)
    except Exception as e:
        print(e)