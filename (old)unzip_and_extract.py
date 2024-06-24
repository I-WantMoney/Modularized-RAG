import s3fs
import zipfile
import io
import os
import boto3
from langchain_community.document_loaders import UnstructuredFileLoader
# import time

# S3の一時バケットとパスの指定
temp_bucket = "lxj-temp-bucket"
temp_folder = "temp_folder/"
# S3ファイルシステムクライアントを作成

s3 = s3fs.S3FileSystem()
s3boto = boto3.client('s3')

def unzip_extract(s3_uri:str):
    # start_time = time.time()
    
    bucket_name, zip_file_path = s3_uri.replace("s3://", "").split("/", 1)
        # 一時フォルダの指定
    temp_dir = "temp_uploadedfiles"
    

    # if not os.path.exists(temp_dir):
    #     os.makedirs(temp_dir)
    
    # ドキュメントを格納するリストを初期化
    s3_raw_doc = []
    # ZIPファイルをバイナリモードで読み込む
    with s3.open(f"{bucket_name}/{zip_file_path}", "rb") as zip_file:
        # ZIPファイルをメモリ上に展開
        zip_data = io.BytesIO(zip_file.read())
        
        # ZIPファイルを解凍
        with zipfile.ZipFile(zip_data, "r") as zip_ref:
            # ZIPファイル内のすべてのファイルをループして処理
            print(zip_ref.namelist())
            for file_name in zip_ref.namelist():
                # S3の一時フォルダにファイルを展開
                # print(file_name)
                if file_name.endswith(".xlsx") or file_name.endswith(".pdf") or file_name.endswith(".docx"):
                    s3_temp_file_path = f"{temp_bucket}/{temp_folder}{os.path.basename(file_name)}"
                    
                    print(s3_temp_file_path)
                    with s3.open(s3_temp_file_path, "wb") as s3_temp_file:
                        s3_temp_file.write(zip_ref.read(file_name))

                        # ローカルの一時ファイル名を取得
                        local_temp_file_name = os.path.basename(file_name)
                        temp_filepath = os.path.join(temp_dir, local_temp_file_name)
                        
                    # S3上の一時ファイルのuri取得
                    s3_temp_file_path_uri = f"s3://{s3_temp_file_path}"
                    
                    temp_bucket_name, temp_object_key = s3_temp_file_path_uri.replace("s3://", "").split("/", 1)
                    s3boto.download_file(temp_bucket_name, temp_object_key, temp_filepath)
                    
                    try:
                        # ローカルの一時ファイルからテキスト抽出
                        loader = UnstructuredFileLoader(temp_filepath)
                        docs = loader.load()
                        s3_raw_doc += docs
                        
                    finally:
                        # ローカルの一時ファイルを削除
                        os.remove(temp_filepath)
                else:
                    docs = []
                    s3_raw_doc += docs
                    
                print(docs)
                
                # S3上の一時ファイルを削除
                s3boto.delete_object(Bucket=temp_bucket,Key = f'{temp_folder}{os.path.basename(file_name)}')
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(f"実行時間: {execution_time:.2f}秒")
    return s3_raw_doc

# a = unzip_extract("s3://lxj-destnation-bucket/uploads/test_zipfile.zip")
# print(a)