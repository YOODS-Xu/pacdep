#analyze bmp file

def main(fnm):
    # bmpファイルをバイナリモードで読み込み
    file = open(fnm,"rb")
    data = file.read()
    file.close()
    
    # ヘッダ部の情報を切り分け
    format_type = data[0:2] # 画像フォーマットの種類を取得
    file_size = data[2:6] # ファイルサイズを取得
    header_size = data[10:14] # ヘッダサイズを取得
    width, height = data[18:22], data[22:26] # 画像の高さと幅を取得
    color_bit = data[28:30] # 1画素の色数を取得  
    
    # リトルエンディアン方式で16進数から10進数に変換
    file_size = int.from_bytes(file_size, 'little')
    header_size = int.from_bytes(header_size, 'little')
    width = int.from_bytes(width, 'little')
    height = int.from_bytes(height, 'little')  
    color_bit = int.from_bytes(color_bit, 'little') 
    
    # ヘッダ情報をコンソール出力
    print("Format type:", format_type)
    print("File size:", file_size, "[byte]")
    print("Header size:", header_size, "[byte]") 
    print("Width:", width, "[px]")     
    print("Height:", height, "[px]")
    print("Total pixels:", width*height)  
    print("Color:", color_bit, "[bit]")  
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Analyze bmp file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file_name', help='name of bmp file', default='sample.bmp', type=str)
    
    args = parser.parse_args()
    
    try:
        main(args.file_name)
    except Exception as e:
        print(e)