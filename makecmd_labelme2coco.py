#子ディレクトリの全部に対して、coco変換コマンド出力

import os
from pathlib import Path
    
     
def main(input_dir, output_dir):
    """変換メイン
    Args:
        input_dir(string): 変換前のディフォルト
        output_dir(string): 変換後のディフォルト
 
    Raises:
        FileExistsError: 出力先ディレクトリが既に存在した場合に生じます
    """
       
    subdir_list = [dir_name for dir_name in os.listdir(input_dir) if os.path.isdir(Path(input_dir).joinpath(dir_name))]
    
    for dir_name in subdir_list:
        input_path_name = Path(input_dir).joinpath(dir_name)
        output_path_name = Path(output_dir).joinpath(dir_name)
        
        print("python labelme-4.6.0/examples/instance_segmentation/labelme2coco.py --labels all_backup/Files/labels_bag.txt ", str(input_path_name), " ", str(output_path_name))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Make labelme2coco commands',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input_dir', help='Directory of resource files', default='resource', type=str)
    parser.add_argument('--output_dir', help='Directory of coco files', default='coco', type=str)
            
    args = parser.parse_args()
    
    try:
        main(args.input_dir, args.output_dir)
    except Exception as e:
        print(e)