import s3fs
import zipfile
import io
import os
import re
import boto3
import streamlit as st
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.docstore.document import Document

# S3バケットとZIPファイルのパスを指定
# bucket_name = "lxj-lambda-code-bucket"
# zip_file_path = "fastapi-app/test_zipfile.zip"
temp_bucket = "lxj-temp-bucket"
temp_folder = "temp_folder/"
# S3ファイルシステムクライアントを作成

s3 = s3fs.S3FileSystem()
delete_file = boto3.client('s3')

def unzip_extract(s3_uri:str):
    match = re.match(r's3://([^/]+)/(.+)', s3_uri)
    print(match)
    if match:
        bucket_name = match.group(1)
        zip_file_path = match.group(2)
    # ドキュメントを格納するリストを初期化
    s3_raw_doc = []
    # ZIPファイルをバイナリモードで読み込む
    with s3.open(f"{bucket_name}/{zip_file_path}", "rb") as zip_file:
        # ZIPファイルをメモリ上に展開
        zip_data = io.BytesIO(zip_file.read())
        
        # ZIPファイルを解凍
        with zipfile.ZipFile(zip_data, "r") as zip_ref:
            # ZIPファイル内のすべてのファイルをループして処理
            for file_name in zip_ref.namelist():
                # S3の一時フォルダにファイルを展開
                # print(file_name)
                if file_name.endswith(".xlsx"):
                    s3_temp_file_path = f"{temp_bucket}/{temp_folder}{os.path.basename(file_name)}"
                    print(s3_temp_file_path)
                    with s3.open(s3_temp_file_path, "wb") as s3_temp_file:
                        s3_temp_file.write(zip_ref.read(file_name))
                    loader = UnstructuredFileLoader(f"s3://{s3_temp_file_path}")
                    docs = loader.load()
                else:
                    docs = []
                    st.info(f":red[_Attention,{file_name} in the Zip is not readable at present._]")
                    # print(f"{file_name} is not readable at present")
                print(docs)
                s3_raw_doc += docs
                delete_file.delete_object(Bucket=temp_bucket,Key = f'{temp_folder}{os.path.basename(file_name)}')
    
    return s3_raw_doc