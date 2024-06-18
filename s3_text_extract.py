# excelファイルのみ対応可能、原因不明
from langchain_community.document_loaders import UnstructuredFileLoader
from unzip_and_extract import unzip_extract
import streamlit as st
import boto3
import re
s3 = boto3.client('s3')

def get_text_from_s3_file(s3_uri:str):
    
    if st.session_state.uri_s != s3_uri:
        st.session_state.uri_s = s3_uri
        print("We got a new S3 URI")
        # uriがファイルの場合(今はxlsxのみ対応可能)
        if s3_uri.endswith(".xlsx") or s3_uri.endswith(".pdf") or s3_uri.endswith(".docx"):
            filepath = s3_uri
            loader = UnstructuredFileLoader(filepath)
            docs = loader.load()
            s3_raw_doc = docs
            
        # zipの場合
        elif s3_uri.endswith(".zip"):
            s3_raw_doc = unzip_extract(s3_uri)
            
        # uriがフォルダの場合
        else:
            s3_raw_doc = []
            match = re.match(r's3://([^/]+)/(.+)',s3_uri)
            print(match)
            if match:
                s3_bucket = match.group(1)
                print(s3_bucket)
                s3_folder_path = match.group(2)
                print(s3_folder_path)
                response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_folder_path)
                file_names = []
                print(response)
                for obj in response['Contents']:
                    file_name=obj['Key'].split('/')[-1]
                    if file_name:
                        file_names.append(file_name)
                for file in file_names:
                    file = str(file)
                    if file.endswith(".xlsx") or s3_uri.endswith(".pdf") or s3_uri.endswith(".docx"):
                        file_path = s3_uri + file
                        loader = UnstructuredFileLoader(file_path)
                        docs = loader.load()
                        s3_raw_doc += docs
                    else:
                        continue   
        # リンクの変わらない場合、空listにする
    else:
        s3_raw_doc = []
    return s3_raw_doc



# from langchain_community.document_loaders import UnstructuredFileLoader
# import streamlit as st

# def get_text_from_s3_file(s3_uri):
#     if st.session_state.uri_s != s3_uri:
#         st.session_state.uri_s = s3_uri
#         print("We got a new S3 file")
#         filepath = s3_uri
#         loader = UnstructuredFileLoader(filepath)
#         docs = loader.load()
#         s3_raw_doc = docs
#     # リンクの変わらない場合、空listにする
#     else:
#         s3_raw_doc = []
#     return s3_raw_doc
