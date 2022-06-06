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
    print(dir_name + ":")
    print()
    command = "python iview_fn.py result_backup/result_22.03.11_all_200_gray sample_data/MrHarada/AspectRatio_corr/"
    command += dir_name + "/JPEGImages --anno_file sample_data/MrHarada/AspectRatio_corr/"
    command += dir_name + "/annotations.json"
    print(command)
    print()
    print()
    