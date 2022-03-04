#カラー画像をグレースケール化
#コマンドラインで指定↓
#カラーファイルディレクトリ:input_dir(デフォルト:selected_data)
#グレースケールファイルディレクトリ:output_dir(デフォルト：gray)
#アルゴリズム：cvtcolor(ディフォルト、コマンドラインで指定なしの場合)かdecolor(コマンドラインで--decolor)

import os
import shutil
import cv2

from pathlib import Path

IMAGE_FILE_EXT = "JPG"
JSON_FILE_EXT = "json"

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
        path_name = Path(input_dir).joinpath(dir_name)
        if not path_name.exists():
            raise OSError(2, "No such directory", str(path_name))
        
def main(input_dir, output_dir, algorithm):
    """変換メイン
    Args:
        input_dir(string): 変換前カラー画像のディフォルト
        output_dir(string): 変換後グレースケール画像のディフォルト
        algorithm(string): アルゴリズムcvtcolor(ディフォルト)かdecolor

    Raises:
        FileExistsError: 出力先ディレクトリが既に存在した場合に生じます
    """
    
    #inputカラー画像ディフォルトの存在チェック
    check_dir(input_dir)
    
    dir_list = [ "train", "test" ]    
    
    for dir_name in dir_list:
        input_path_name = Path(input_dir).joinpath(dir_name)
        output_path_name = Path(output_dir).joinpath(dir_name)
        
        #outputグレースケールファイルディレクトリ作成、既に存在した場合、エラー上げて終了
        Path(output_path_name).mkdir(parents=True, exist_ok=False)
        
        #ファイル一覧取得
        files = os.listdir(input_path_name)
        file_name_list = [f for f in files if f[0-len(IMAGE_FILE_EXT):] == IMAGE_FILE_EXT]

        for f in file_name_list:
            img = cv2.imread(str(Path(input_path_name).joinpath(f)))
            
            #グレースケール変換
            if algorithm == "cvtcolor":
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                img_gray, _ =cv2.decolor(img)
                     
            cv2.imwrite(str(Path(output_path_name).joinpath(f)), img_gray)
            
            #jsonファイルのコピー
            json_file_name = f.rstrip(IMAGE_FILE_EXT) + JSON_FILE_EXT
            shutil.copy(Path(input_path_name).joinpath(json_file_name),
                        Path(output_path_name).joinpath(json_file_name))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert color images to gray scale.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input_dir', help='Directory of input color files', default='selected_data', type=str)
    parser.add_argument('--output_dir', help='Directory of output gray scale files', default='gray', type=str)
    parser.add_argument('--decolor', dest='algorithm', action='store_const',
                        const='decolor', default='cvtcolor',
                        help='alogrithm for conversion:decolor')
    
    args = parser.parse_args()
    
    try:
        main(args.input_dir, args.output_dir, args.algorithm)
    except Exception as e:
        print(e)

else: 
    try:
        main(input_dir='selected_data', output_dir='gray', algorithm='cvtcolor')
    except Exception as e:
        print(e)