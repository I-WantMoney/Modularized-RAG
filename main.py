import streamlit as st
from button_setting import click_button
from file_text_extract import get_text_from_file
from s3uri_text_extract import get_text_from_s3_file
from langchain_core.messages import AIMessage, HumanMessage
from chunk_setting import get_chunks
from response_gen import get_response
from vectorDB_create import get_vectorstore

def main():
    # app config
    st.set_page_config(page_title="Chat with your files", page_icon="🤖")
    st.title("Chat with your file(s).")
    st.info("Click the :red[_Process_] button before asking questions (:red[_Only the first time you upload_])\n\n質問する前に:red[Process]ボタンを押してください (:red[最初アプロード時のみ押し必要])")
    
    # ボタンのクリック状態の初期化設定
    if "clicked" not in st.session_state:
        st.session_state.clicked = False   
    
    # ファイル存在情況の初期化
    if "file_s" not in st.session_state:
        st.session_state.file_s = [] 
        
    # S3ファイル存在情況の初期化
    if "uri_s" not in st.session_state: 
        st.session_state.uri_s = None
    
    # ----の初期化
    if "full_doc" not in st.session_state:
        st.session_state.full_doc = []
    # ----の初期化
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
     
    # サイドバーの設定
    with st.sidebar:
        # file upload
        st.title("Settings")
        st.header("",divider="rainbow")
        
        st.subheader("_Upload_ :rainbow[FILE(s)] :books:")
        allfile = st.file_uploader("Upload your FILE(s) here and click on '_Process_'\n\nファイルのをアップして、[_Process_]ボタンをクリック",accept_multiple_files=True,type=["xlsx","docx","pdf"])
        
        st.subheader("_Enter_ a :blue[S3 Bucket URI]:link:\n・xlsx、pdf、docxに対応可能。\n\n・上記ファイルの入っているフォルダ、Zipファイルも対応可能。 ")
        s3_uri = st.text_input("_S3 URI_")
        
        st.header("",divider="blue")
    
    # ボタン
    st.button("Process", on_click=click_button)
    # 最初アップロード時にクリックすれば十分
    # クリックされたら、その状態をセッションに保存  
    if st.session_state.clicked:
        
        if allfile == [] and (s3_uri is None):
            file_existance = False
            file_raw_doc = []
            s3_raw_doc = []
            st.info(":red[_Enter a S3 URI or Upload some files_]\n\n:red[_S3 URIの入力またはファイルのアップロードをしてください_]")
        
        else:
            # ローカルあり、s3なしの場合
            if allfile != [] and (s3_uri is None):
                file_existance = True
                file_raw_doc = get_text_from_file(allfile)
                s3_raw_doc = []
            
            #　ローカルなし、s3ありの場合
            if allfile == [] and (s3_uri is not None):
                file_existance = True
                file_raw_doc = []
                s3_raw_doc = get_text_from_s3_file(s3_uri)
            
            #　ローカルあり、s3ありの場合
            if allfile != [] and (s3_uri is not None):
                file_existance = True
                s3_raw_doc = get_text_from_s3_file(s3_uri)
                file_raw_doc = get_text_from_file(allfile)
                
            full_doc_add = file_raw_doc + s3_raw_doc
            st.session_state.full_doc += full_doc_add
                
            print (f"Added doc: {full_doc_add}")
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = [
                    AIMessage(content = "Hello, I am a a bot"),
                ]
            # 料金節約のために、追加のドキュメントがあるときのみ、Embeddingを執行
            if full_doc_add != []:
                print("new file(s) added")
                print(f"Full doc: {st.session_state.full_doc}")
                chunks = get_chunks(st.session_state.full_doc)
                st.session_state.vector_store = get_vectorstore(chunks)
            else:
                print(st.session_state.full_doc)
                print("no file added")
            
            # ユーザーのクエリーで回答を生成
            user_query = st.chat_input("Try asking something about your files ")
        
            if user_query is not None and user_query != "":
                response = get_response(user_query)
                # ユーザーの質問とAIの回答をセッションに入れる
                st.session_state.chat_history.append(HumanMessage(content=user_query))
                st.session_state.chat_history.append(AIMessage(content=response))

            # 画面上で表示
            for message in st.session_state.chat_history:
                if isinstance(message,AIMessage):
                    with st.chat_message("AI"):
                        st.write(message.content)
                elif isinstance(message,HumanMessage):
                    with st.chat_message("Human"):
                        st.write(message.content)
                     
if __name__ == "__main__":
    main()