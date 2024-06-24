import zipfile
import os
import boto3
from langchain_community.document_loaders import UnstructuredFileLoader
# import time


# s3 = s3fs.S3FileSystem()
s3boto = boto3.client('s3')

def unzip_extract(s3_uri:str):
    # start_time = time.time()
    
    bucket_name, zip_file_path = s3_uri.replace("s3://", "").split("/", 1)
    # 一時フォルダの指定
    temp_dir = "temp_uploadedfiles"
    
    # 一時フォルダが存在しない場合のみ作成
    # if not os.path.exists(temp_dir):
    #     os.makedirs(temp_dir)
    
    # ドキュメントを格納するリストを初期化
    s3_raw_doc = []
    
    # ZIPファイルをローカルにダウンロード
    local_zip_file_path = os.path.join(temp_dir, os.path.basename(zip_file_path))
    s3boto.download_file(bucket_name, zip_file_path, local_zip_file_path)
    
    # ZIPファイルを解凍
    with zipfile.ZipFile(local_zip_file_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
        
    # 解凍されたファイルを処理
    for root, dirs, files in os.walk(temp_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            print("local file path is: "+ file_path)
            if file_name.endswith(".xlsx") or file_name.endswith(".pdf") or file_name.endswith(".docx"):
                try:
                    # ローカルのファイルからテキスト抽出
                    loader = UnstructuredFileLoader(file_path)
                    docs = loader.load()
                    s3_raw_doc += docs
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
            else:
                docs = []
                s3_raw_doc += docs
    
    # 一時ファイルとディレクトリを削除
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file_name in files:
            os.remove(os.path.join(root, file_name))
        for dir_name in dirs:
            os.rmdir(os.path.join(root, dir_name))
    # os.rmdir(temp_dir)
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(f"実行時間: {execution_time:.2f}秒")
    
    return s3_raw_doc

# a = unzip_extract("s3://lxj-destnation-bucket/uploads/test_zipfile.zip")
# print(a)