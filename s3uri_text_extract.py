from langchain_community.document_loaders import UnstructuredFileLoader
import streamlit as st
import boto3
import os
from unzip_and_extract import unzip_extract
s3 = boto3.client('s3')

def get_text_from_s3_file(s3_uri:str):
    docs = []
    if st.session_state.uri_s != s3_uri:
        st.session_state.uri_s = s3_uri
        if s3_uri.startswith("s3://"):
            print("We got a new S3 URI")
            
            # 一時フォルダの指定
            temp_dir = "temp_uploadedfiles"
            # if not os.path.exists(temp_dir):
            #     os.makedirs(temp_dir)
            
            # uriがファイルの場合(今はxlsx、pdf、docxのみ対応可能)
            if s3_uri.endswith(".xlsx") or s3_uri.endswith(".pdf") or s3_uri.endswith(".docx"):
                bucket_name, object_key = s3_uri.replace("s3://", "").split("/", 1)
                file_name = os.path.basename(object_key)
                temp_filepath = os.path.join(temp_dir, file_name)
                s3.download_file(bucket_name, object_key, temp_filepath)
                
                try:
                    loader = UnstructuredFileLoader(temp_filepath)
                    docs = loader.load()
                finally:
                    os.remove(temp_filepath)
                    
            # ZIPの場合
            elif s3_uri.endswith(".zip"):
                docs = unzip_extract(s3_uri)
                
            # uriがフォルダの場合
            else:
                docs = []
                s3_bucket, s3_folder_path = s3_uri.replace("s3://", "").split("/", 1)
                print(s3_bucket)
                print(s3_folder_path)
                response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_folder_path)
                file_names = []
                print(response)
                for obj in response['Contents']:
                    file_name = obj['Key'].split('/')[-1]
                    if file_name:
                        file_names.append(file_name)
                print(file_names)
                for file in file_names:
                    file = str(file)
                    if file.endswith(".xlsx") or file.endswith(".pdf") or file.endswith(".docx"):
                        file_path = f"s3://{s3_bucket}/{s3_folder_path}{file}"
                        bucket_name, object_key = file_path.replace("s3://", "").split("/", 1)
                        temp_filepath = os.path.join(temp_dir, file)
                        s3.download_file(bucket_name, object_key, temp_filepath)

                        try:
                            loader = UnstructuredFileLoader(temp_filepath)
                            temp_doc = loader.load()
                            docs += temp_doc
                        finally:
                            os.remove(temp_filepath)
                    else:
                        temp_doc=[]
                        docs += temp_doc
                        continue
        # s3のuriじゃない場合、空listにする            
        elif (s3_uri is None) or (s3_uri == ""):
            docs = []
        else:
            docs = []
            st.info(":red[_This is not an S3 uri, Please check_]")
    # リンクの変わらない場合、空listにする
    else:
        docs = []
    s3_raw_doc = docs
    return s3_raw_doc