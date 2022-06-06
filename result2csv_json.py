#result→csv
#コマンドラインで指定↓
#dir(デフォルト:result_json)
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
    for i in range(2):
        for j in range(3):
            col = type[i] + val[j]
            col_list.append(col)
            
    df = pd.DataFrame(columns=col_list)

    #ファイル一覧取得
    file_name_list = [f for f in os.listdir(dir) if f.endswith(".json")]
    file_path_list = [str(Path(dir).joinpath(f)) for f in file_name_list]

    i = 0
    for f in file_path_list:    
        with open(f, 'r') as jsonfile:
            dic_result = json.load(jsonfile)     
            df.at[i,"filename"] = file_name_list[i].replace(".json", "")
            for m in range(2):
                for n in range(3):
                    col = type[m] + val[n] 
                    #df.at[i, col] = round(dic_result[type[m]][val[n]],2)
                    df.at[i, col] = dic_result[type[m]][val[n]]
        i += 1
        jsonfile.close
    
    print(df)
    
    df.to_csv(str(Path(dir).joinpath("result.csv")), index = False)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='result_json to csvfile.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir', help='Directory of input files', default='result_json', type=str)
    parser.add_argument('--csvfile', help='result csv file', default='result.csv', type=str)
        
    args = parser.parse_args()
    
    try:
        main(args.dir, args.csvfile)
    except Exception as e:
        print(e)