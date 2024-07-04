import streamlit as st
from button_setting import click_button
from file_text_extract import get_text_from_file
from s3uri_text_extract import get_text_from_s3_file
from langchain_core.messages import AIMessage, HumanMessage
from chunk_setting import get_chunks
from response_gen import rag_get_response,qa_get_response
from vectorDB_create import get_vectorstore
import os
# new----------------------------
import uuid
# -------------------------------

def main():
    
    # 一時フォルダの指定
    temp_dir = "temp_uploadedfiles"
    # 一時フォルダが存在しない場合のみ作成
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)   
        
    # app config
    st.set_page_config(page_title="Chat with your files", page_icon="🤖")
    st.title("Chat with your file(s).")
    
    
    # ボタンのクリック状態の初期化設定
    if "clicked" not in st.session_state:
        st.session_state.clicked = False   
    
    # セッション状態にセッションIDが存在しない場合、初期化
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # ファイル存在情況の初期化
    if "file_s" not in st.session_state:
        st.session_state.file_s = [] 
        
    # S3ファイル存在情況の初期化
    if "uri_s" not in st.session_state: 
        st.session_state.uri_s = None
    
    # 会話履歴の初期化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content = "Hello, I am a bot"),
        ]
    
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
        
        st.info("Click the :red[_Process_] button before chatting with files (:red[_Only the first time you upload_])\n\n:red[ファイルに質問する]前に:red[Process]ボタンを押してください (:red[最初アプロード時のみ押し必要])")
        # ボタン
        st.button("Process", on_click=click_button)
        # 最初アップロード時にクリックすれば十分    
        
        st.subheader("_Upload_ :rainbow[FILE(s)] :books:")
        allfile = st.file_uploader("Upload your FILE(s) here and click on '_Process_'\n\nファイルのをアップして、[_Process_]ボタンをクリック",accept_multiple_files=True,type=["xlsx","docx","pdf"])
        
        st.subheader("_Enter_ a :blue[AWS S3 Bucket URI]:link:\n・xlsx、pdf、docxに対応可能。\n\n・上記ファイルの入っているフォルダ、Zipファイルも対応可能。 ")
        s3_uri = st.text_input(label="_AWS S3 URI_",value=st.session_state.uri_s)
        
        st.header("",divider="blue")
    
    user_query = st.chat_input("Chat with AI ")
    
    # アプロードなしの場合 ----------------------------------
    if (allfile == [] and (s3_uri is None)) or st.session_state.clicked == False:
        st.info(":green[_Nothing is upoaded yet, but you can still chat with AI._]\n\n:green[_まだ何もアップされていないですが、AIとの会話が可能です_]")
        if (user_query is not None) and (user_query != ""):
            res = qa_get_response(user_query)
            response = res.content
            st.session_state.chat_history.append(HumanMessage(content=user_query))
            st.session_state.chat_history.append(AIMessage(content=response))
    # -----------------------------------------------------

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
                try:
                    s3_raw_doc = get_text_from_s3_file(s3_uri)
                except:
                    st.info(":red[_This is not an S3 uri, Please check_]")
                    s3_raw_doc =[]

            #　ローカルあり、s3ありの場合
            if allfile != [] and (s3_uri is not None):
                file_existance = True
                try:
                    s3_raw_doc = get_text_from_s3_file(s3_uri)
                except:
                    st.info(":red[_This is not an S3 uri, Please check_]")
                    s3_raw_doc =[]
                    
                file_raw_doc = get_text_from_file(allfile)
                
        full_doc_add = file_raw_doc + s3_raw_doc
        st.session_state.full_doc += full_doc_add 

        if st.session_state.full_doc == []:
            print("no file added")
            # print(f"Full doc: {st.session_state.full_doc}")
            st.info(":green[_Nothing is upoaded yet, but you can still chat with AI._]\n\n:green[_まだ何もアップされていないですが、AIとの会話が可能です_]")
            
            if (user_query is not None) and (user_query != ""):
                res = qa_get_response(user_query)
                response = res.content
                st.session_state.chat_history.append(HumanMessage(content=user_query))
                st.session_state.chat_history.append(AIMessage(content=response))
                    
        # 料金節約のために、追加のドキュメントがあるときのみ、Embeddingを執行
        if full_doc_add != [] or st.session_state.full_doc != []:
            # print("new file(s) added")
            # print(f"Full doc: {st.session_state.full_doc}")
            chunks = get_chunks(st.session_state.full_doc)
            st.session_state.vector_store = get_vectorstore(chunks)
        
            if (user_query is not None) and (user_query != ""):
                res = rag_get_response(user_query)
                response = res['answer']
                
                # reshistory = res['chat_history']
                # try:
                #     print(f"res_history is {reshistory}")
                # except:
                #     print("reshistory not ok")
                
                # ユーザーの質問とAIの回答をセッションに入れる
                # st.session_state.chat_history = reshistory
                st.session_state.chat_history.append(HumanMessage(content=user_query))
                st.session_state.chat_history.append(AIMessage(content=response))

    # 画面上で会話履歴を表示
    for message in st.session_state.chat_history:
        if isinstance(message,AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message,HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
    print(f"session state: {st.session_state}")
    
if __name__ == "__main__":
    main()