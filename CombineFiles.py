#各フォルダからランダムにデータファイルを選び、合せデータを作成
#コマンドラインから下記引数を指定
#合せる前のディレクトリ:resource_dir(デフォルト:resourceData)
#合せた後のディレクトリ：combination_dir(デフォルト：allData)
#合せデータの画像数：dataset_img_number(デフォルト：50)＊JSONファイルもあるから、ファイル数はこの倍
#各フォルダから選ぶ数：dataset_number/(フォルダ数-1)
#足りないファイルはresource_dir/ADDから取得（ADDは前準備で一番多いフォルダから一部切出して作成）

import os
import sys
import glob
import shutil
import random as rd

def main(resource_dir, combination_dir, dataset_img_number):
    """合せメイン
    Args:
        resource_dir(string):合せる前の各ディレクトリの格納ディレクトリ
        combination_dir(string):合せた後の出力先ディレクトリ
        dataset_img_number(int):データセットの画像数
    
    Raises:
        FileExistsError:合せた後の出力先ディレクトリが存在する場合に生じます。
    """

    #合せる前の格納ディレクトの存在チェック
    if not os.path.exists(resource_dir):
        raise OSError(2, "No such directory", resource_dir)
    
    #合せた後ファイル出力先ディレクトを作成します
    os.makedirs(combination_dir, exist_ok=False)

    #resource_dirのディレクト一覧を取得
    dir_list = os.listdir(resource_dir)
    dir_num = len(dir_list)
    
    #各フォルダから選ぶ画像数を計算、ADDがあるからフォルダ数-1で割る
    select_img_num = dataset_img_number // (dir_num - 1)
    img_sum_num = 0
    
    for i in range(dir_num):
        if dir_list[i] != "ADD":
            file_list = glob.glob(os.path.join(resource_dir, dir_list[i], '*.JPG'))
            file_num = len(file_list)
            
            if file_num >= select_img_num:
                action_num = select_img_num
            else:
                action_num = file_num
                
            selected_files = rd.sample(file_list, action_num)            
            img_sum_num += action_num

            for j in range(action_num):
                #JPGファイルのコピー
                file_path_before = selected_files[j]
            
                #ファイル名だけ取出す
                file_path_after = os.path.join(combination_dir, selected_files[j].lstrip(os.path.join(resource_dir, dir_list[i])))
                shutil.copy(file_path_before, file_path_after)

                #JSONファイルのコピー
                file_path_before = os.path.join(selected_files[j].rstrip("JPG") + "JSON")
                file_path_after = os.path.join(combination_dir, selected_files[j].lstrip(os.path.join(resource_dir, dir_list[i])).rstrip("JPG") + "JSON")
                shutil.copy(file_path_before, file_path_after)
    
    #不足分をADDフォルダから取得
    img_diff_num = dataset_img_number - img_sum_num
    if img_diff_num > 0:
        file_list = glob.glob(os.path.join(resource_dir, "ADD", '*.JPG'))
        selected_files = rd.sample(file_list, img_diff_num)
        for j in range(img_diff_num):
            #JPGファイルのコピー
            file_path_before = selected_files[j]
            
            #ファイル名だけ取出す
            file_path_after = os.path.join(combination_dir, selected_files[j].lstrip(os.path.join(resource_dir, "ADD")))
            shutil.copy(file_path_before, file_path_after)

            #JSONファイルのコピー
            file_path_before = os.path.join(selected_files[j].rstrip("JPG") + "JSON")
            file_path_after = os.path.join(combination_dir, selected_files[j].lstrip(os.path.join(resource_dir, "ADD")).rstrip("JPG") + "JSON")
            shutil.copy(file_path_before, file_path_after)
           

 
 
        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Combine files.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--resource_dir', help='Directory of resource files', default='resource', type=str)
    parser.add_argument('--combination_dir', help='Directory of combination files', default='allData', type=str)
    parser.add_argument('--dataset_img_number', help='File Number of Dataset ', default=50, type=int)
    
    args = parser.parse_args()
    
    try:
        main(args.resource_dir, args.combination_dir, args.dataset_img_number)
    except Exception as e:
        print(e)