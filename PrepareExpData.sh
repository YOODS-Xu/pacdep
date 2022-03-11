#!/bin/bash
if [ $# != 1 ]; then
    echo データセット画像数指定エラー: $*
    exit 1
else
    #合せデータ作成
    python CombineFiles.py --dataset_img_number $1
    
    #8:2の割合でtrainとtestに振り分け
    python RandomlySelectFile_2types.py

    #coco変換
    python labelme-4.6.0/examples/instance_segmentation/labelme2coco.py --labels all_backup/Files/labels_bag.txt selected_data/train coco/train
    python labelme-4.6.0/examples/instance_segmentation/labelme2coco.py --labels all_backup/Files/labels_bag.txt selected_data/test coco/test

    rm -r allData
    rm -r selected_data
fi