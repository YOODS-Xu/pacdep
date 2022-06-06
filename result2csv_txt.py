#ディレクトリ下の*.txt（出力結果）から各評価指標値を読み取り、csvファイルに出力
#コマンドラインで指定↓
#dir(デフォルト:result_txt)
#csvfile(デフォルト：result.csv)

import os
from pathlib import Path
import json
import pandas as pd


def main(dir, csvfile):
    """メイン
    Args:
        dir(string): 
        csvfile
       """
    
    type = ["bbox", "segm"]
    val = ["AP", "AP50", "AP75", "AR1", "AR10", "AR100"]
    col_list = ["filename"]
    keyword_list = ["(AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]", 
                    "(AP) @[ IoU=0.50      | area=   all | maxDets=100 ]", 
                    "(AP) @[ IoU=0.75      | area=   all | maxDets=100 ]", 
                    "(AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ]", 
                    "(AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ]", 
                    "(AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]"]

    for i in range(2):
        for j in range(6):
            col = type[i] + val[j]
            col_list.append(col)
            
    df = pd.DataFrame(columns=col_list)

    #ファイル一覧取得
    file_name_list = [f for f in os.listdir(dir) if f.endswith(".txt")]
    file_path_list = [str(Path(dir).joinpath(f)) for f in file_name_list] 

    i = 0
    for f in file_path_list:    
        with open(f, 'r') as txtfile:
            #バンディングボックスかセグメンテーションかを判断
            for line_str in txtfile.readlines():
                if line_str.find("*bbox*") > 0:
                    m = 0
                elif line_str.find("*segm*") > 0:
                    m = 1

                col = "null"
                #評価値があるかどうかを判断
                for n in range(6):
                    if line_str.find(keyword_list[n]) > 0:
                        col = type[m] + val[n]
                  
                if col != "null":
                    val_start = line_str.rfind("=") + 2

                    #df.at[i, col] = round(line_str[val_start:0],2)
                    df.at[i, col] = line_str[val_start:].strip()

        df.at[i,"filename"] = file_name_list[i].replace(".txt", "")
            
        #1ファイルが1行
        i += 1
        txtfile.close
    
    df.to_csv(str(Path(dir).joinpath(csvfile)), index = False)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='result_txt to csvfile.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', help='Directory of input files', default='result_txt', type=str)
    parser.add_argument('--csvfile', help='result csv file', default='result.csv', type=str)
        
    args = parser.parse_args()
    
    try:
        main(args.dir, args.csvfile)
    except Exception as e:
        print(e)