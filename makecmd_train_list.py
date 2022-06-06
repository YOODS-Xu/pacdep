#modeltest コマンド出力
from importlib.util import module_for_loader
import os
from pathlib import Path

import argparse
parser = argparse.ArgumentParser(
    description='generate train command automatically',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--model', help='model', default='model', type=str)
args = parser.parse_args()

#コマンドライン引数から取得
#model = args.model

#作りこみ
#model_main = "mogi160_gray+factory100"
    
dataset_list = ["factory_160", "mogi_40factory_120", "mogi_80factory_80", "mogi_120facotory_40"]
    
for dataset in dataset_list:
    command = "mv sample_data/fullPac/mix/" + dataset + " sample_data/fullPac/mix/train"
    print(command)

    model = "result_22.04.20fullPac_" + dataset
    command = "python translearn.py sample_data/fullPac/mix result_backup/" + model
    command += " &> result_backup/ScreenOutput/ScreenOutput22.04.20fullPac_"
    command +=  dataset + ".txt"
 
    print(command)

    command = "mkdir result_backup/" + model +"/coco"
    print(command)

    command = "cp -r sample_data/fullPac/mix/train result_backup/" + model +"/coco"
    print(command)
    command = "cp -r sample_data/fullPac/mix/test result_backup/" + model +"/coco"
    print(command)
    
    command = "mv sample_data/fullPac/mix/train" + " sample_data/fullPac/mix/" + dataset
    print(command)