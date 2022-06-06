#modeltest コマンド出力
from importlib.util import module_for_loader
import os
from pathlib import Path

import argparse
parser = argparse.ArgumentParser(
    description='generate modeltest command automatically',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--model', help='model', default='model', type=str)
args = parser.parse_args()

#コマンドライン引数から取得
#model = args.model

#作りこみ
#model = "result_22.04.06_mogi160_gray+factory100"
#model_main = "mogi160_gray+factory100"
    
dataset_list = ["mogi_fullPac_gray_160-4nonDet"]
    
for dataset in dataset_list:
    command = "mv sample_data/fullPac/mix/" + dataset + " sample_data/fullPac/mix/train"
    print(command)

    model = "_22.04.20fullPac_" + dataset
    command = "python modeltest.py sample_data/fullPac/mix result_backup/result" + model
    command +=  " result_backup/modeltest/modeltest" + model + "_"
    command += "factory100_hkoAB_23m_2t_3tl_3"
    command += " &> result_backup/ScreenOutput/modeltest/ScreenOutput" + model + "_"
    command +=  "factory100_hkoAB_23m_2t_3tl_3.txt"
 
    print(command)
    
    command = "mv sample_data/fullPac/mix/train" + " sample_data/fullPac/mix/" + dataset
    print(command)