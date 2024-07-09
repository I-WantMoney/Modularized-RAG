import os
import streamlit as st
from langchain_community.document_loaders import UnstructuredFileLoader

current_dir = os.path.dirname(os.path.abspath(__file__))

def get_text_from_file(allfile):
    temp_dir = "temp_uploadedfiles"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    text_list = []
    # セッション内のfile_sと比較して、新しく追加されたファイルのみをテキストに変換
    temp_file = st.session_state.file_s
    if st.session_state.file_s != allfile:
        st.session_state.file_s = allfile
        print("We got new file(s)")
        for file in allfile:
            if file not in temp_file:
                # if file.name.endswith("docx") or file.name.endswith("pdf") or file.name.endswith("xlsx"):
                if file.name.endswith(".pli"):
                    try:
                        original_file_path = os.path.join(current_dir,"temp_uploadedfiles",file.name)
                        file_path = os.path.splitext(original_file_path)[0] + ".txt"
                        with open(original_file_path, "wb") as f:
                            f.write(file.getbuffer())
                        with open(original_file_path,"r") as pli_file:
                            content = pli_file.read()
                        with open(file_path,"w") as txt_file:
                            txt_file.write(content)
                        os.remove(original_file_path)
                    except:
                        print("Not ok")
                    
                else:
                    file_path = os.path.join(current_dir,"temp_uploadedfiles",file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                loader = UnstructuredFileLoader(file_path)
                file_doc = loader.load()
                text_list += file_doc
                
                os.remove(file_path)
        file_raw_doc = text_list
    #　追加ファイルのない場合、空listにする
    else:
        file_raw_doc = []
        
    return file_raw_doc