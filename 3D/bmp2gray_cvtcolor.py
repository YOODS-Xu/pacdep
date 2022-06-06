#bmpカラー画像をグレースケール化:単独ディレクトの全bmpファイル
#コマンドラインで指定↓
#カラーファイルディレクトリ:input_dir(デフォルト:color)
#グレースケールファイルディレクトリ:output_dir(デフォルト：gray)
#アルゴリズム：cvtcolor(作りこみ)

import os
import shutil
import cv2
from pathlib import Path
from glob import glob

IMAGE_FILE_EXT = "bmp"

def check_dir(input_dir):
    """ディレクトリの存在チェック
    Args:
        input_dir(string): 変換前カラー画像のディレクトリ

    Raises:
        OSError: 変換前ディレクトリが存在しない場合に生じます
    """
    #変換前ディレクトリの存在をチェック
    path_name = Path(input_dir)

    if not path_name.exists():
        raise OSError(2, "No such directory", str(path_name))
    
    
        
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
    
    input_path_name = Path(input_dir)
    output_path_name = Path(output_dir)
        
    #outputグレースケールファイルディレクトリ作成、既に存在した場合、エラー上げて終了
    Path(output_path_name).mkdir(parents=True, exist_ok=False)
        
    #ファイル一覧取得
    file_name_list = [f for f in os.listdir(input_path_name) if f.endswith(IMAGE_FILE_EXT)]

    for f in file_name_list:
        img = cv2.imread(str(Path(input_path_name).joinpath(f)))
            
        #グレースケール変換
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                      
        cv2.imwrite(str(Path(output_path_name).joinpath(f)), img_gray)
            



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