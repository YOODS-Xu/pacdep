#modeltest コマンド出力
import os
from pathlib import Path

import argparse
parser = argparse.ArgumentParser(
    description='generate modeltest command automatically',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--dir', help='directory of dataset', default='resource', type=str)
args = parser.parse_args()

input_dir = args.dir
    
subdir_list = [dir_name for dir_name in os.listdir(input_dir) if os.path.isdir(Path(input_dir).joinpath(dir_name))]
    
for dir_name in subdir_list:
    command = "mv sample_data/factory/AspectRatio_corr/" + dir_name + " sample_data/factory/AspectRatio_corr/test"
    print(command)

    command = "python modeltest.py sample_data/factory/AspectRatio_corr result_backup/ result_backup/modeltest/modeltest_22.03.31_mogi_160-factory_"
    command += dir_name + "_AspectRation_corr_100"
    command += " &> result_backup/ScreenOutput/modeltest/ScreenOutput22.03.31_mogi_160-factory_"
    command +=  dir_name + "_AspectRation_corr_100.txt"
 
    print(command)
    
    command = "mv sample_data/factory/AspectRatio_corr/test" + " sample_data/factory/AspectRatio_corr/" + dir_name
    print(command)