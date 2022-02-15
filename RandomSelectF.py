#ランダムにallDataフォルダのファイルを
#TRAIN_DIR、TEST_DIR、VAL_DIRディレクトリに
#RATIO_TRAIN(60)、RATIO_TEST(20)、100-RATIO_TRAIN-RATIO_TESTの率で振り分ける

import os
import sys
import numpy as np
import numpy.random as rd

ALL_DATA_DIR = "allData"
TRAIN_DIR = "selected_data/train"
TEST_DIR = "selected_data/test"
VAL_DIR = "selected_data/val"
IMAGE_FILE_EXT = "JPG"
JSON_FILE_EXT = "json"
RATIO_TRAIN = 60
RATIO_TEST = 20

CURR_PATH = "./"

#ディレクトの存在確認
if os.path.isdir(CURR_PATH + TRAIN_DIR):
    print(TRAIN_DIR + "は既に存在しますので、処理せず終了しました")
    sys.exit(1)

if os.path.isdir(CURR_PATH + TEST_DIR):
    print(TEST_DIR +"は既に存在しますので、処理せず終了しました")
    sys.exit(1)

if os.path.isdir(CURR_PATH + VAL_DIR):
    print(VAL_DIR + "は既に存在しますので、処理せず終了しました")
    sys.exit(1)

#ディレクトリ作成
os.makedirs(CURR_PATH + TRAIN_DIR)
os.makedirs(CURR_PATH + TEST_DIR)
os.makedirs(CURR_PATH + VAL_DIR)

#allDataフォルダのファイル一覧を取得
files = os.listdir(CURR_PATH + ALL_DATA_DIR)

file_name_list = [f for f in files if f[0-len(IMAGE_FILE_EXT):] == IMAGE_FILE_EXT]

num_of_files = len(file_name_list)

num_of_train_files = num_of_files * RATIO_TRAIN // 100
num_of_test_files = num_of_files * RATIO_TEST // 100

num_of_val_files = num_of_files - num_of_train_files - num_of_test_files

fold_list = [None] * num_of_files

for i in range(num_of_train_files):
    fold_list[i] = TRAIN_DIR

for i in range(num_of_train_files, num_of_train_files + num_of_test_files):
    fold_list[i] = TEST_DIR

for i in range(num_of_train_files + num_of_test_files, num_of_files):
    fold_list[i] = VAL_DIR

rd.shuffle(fold_list)

for i in range(num_of_files):
    file_path_before = CURR_PATH + ALL_DATA_DIR + "/" + file_name_list[i]
    file_path_after = CURR_PATH + fold_list[i] + "/" + file_name_list[i]
    os.replace(file_path_before, file_path_after)
    file_path_before = CURR_PATH + ALL_DATA_DIR + "/" + file_name_list[i].rstrip(IMAGE_FILE_EXT) + JSON_FILE_EXT
    file_path_after = CURR_PATH + fold_list[i] + "/" + file_name_list[i].rstrip(IMAGE_FILE_EXT) + JSON_FILE_EXT
    os.replace(file_path_before, file_path_after)



