#ランダムにデータファイルをtrain(80)、test(20)の率で振り分ける
#コマンドラインから下記引数を指定
#振り分け前のディレクトリ:allData_dir(デフォルト:allData)
#振り分け後のディレクトリ：selected_dir(デフォルト：selected_data)

import os
import sys
import random as rd

#模擬袋
#IMAGE_FILE_EXT = "JPG"
#原田智之さんデータ
IMAGE_FILE_EXT = "bmp"
JSON_FILE_EXT = "json"

#振分け比率80:20
RATIO_TRAIN = 80

#シャッフル回数:ランダムのぐらい
SHUFFLE_TIMES = 20


def main(allData_dir, selected_dir):
    """選択メイン
    Args:
        allData_dir(string):選択前ファイルの格納ディレクトリ
        selected_dir(string):選択後ファイル出力先ディレクトリ
    
    Raises:
        FileExistsError:選択後ファイル出力先ディレクトリが存在する場合に生じます。
    """

    #選択前ファイルの格納ディレクトの存在チェック
    if not os.path.exists(allData_dir):
        raise OSError(2, "No such directory", allData_dir)
    
    #選択後ファイル出力先ディレクトを作成します
    dir_list = ["train", "test"]
    for dir_name in dir_list:
        os.makedirs(os.path.join(selected_dir, dir_name), exist_ok=False)

    #allData_dirのファイル一覧を取得
    files = os.listdir(allData_dir)

    file_name_list = [f for f in files if f[0-len(IMAGE_FILE_EXT):] == IMAGE_FILE_EXT]

    num_of_files = len(file_name_list)

    num_of_train_files = num_of_files * RATIO_TRAIN // 100
    num_of_test_files = num_of_files - num_of_train_files

    fold_list = [None] * num_of_files

    for i in range(num_of_train_files):
        fold_list[i] = "train"

    for i in range(num_of_train_files, num_of_train_files + num_of_test_files):
        fold_list[i] = "test"

    for _ in range(SHUFFLE_TIMES):
        rd.shuffle(fold_list)

    for i in range(num_of_files):
        #イメージファイルの移動
        file_path_before = os.path.join(allData_dir, file_name_list[i])
        file_path_after = os.path.join(selected_dir, fold_list[i], file_name_list[i])
        os.replace(file_path_before, file_path_after)
        
        #jsonファイルの移動
        file_path_before = os.path.join(allData_dir, file_name_list[i].replace("." + IMAGE_FILE_EXT, "." + JSON_FILE_EXT))
        file_path_after = os.path.join(selected_dir, fold_list[i], file_name_list[i].replace("." + IMAGE_FILE_EXT, "." + JSON_FILE_EXT))
        os.replace(file_path_before, file_path_after)

        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Select files randomly.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--allData_dir', help='Directory of allData files', default='allData', type=str)
    parser.add_argument('--selected_dir', help='Directory of selected files', default='selected_data', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.allData_dir, args.selected_dir)
    except Exception as e:
        print(e)