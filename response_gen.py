import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv


llm_model = os.environ["OPENAI_API_MODEL"]
load_dotenv()

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI(model=llm_model) # カッコ内でapi-keyの指定、モデルの指定などができます。コードの先頭にdotenvを使ったので、自動的に.envファイルからapi-keyを取得します
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}"),
        ("user","Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    
    retriever_chain = create_history_aware_retriever(llm,retriever,prompt)
    
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    
    llm = ChatOpenAI(model=llm_model) # カッコ内でapi-keyの指定、モデルの指定などができます。コードの先頭にdotenvを使ったので、自動的に.envファイルからapi-keyを取得します
    prompt = ChatPromptTemplate.from_messages([
        ("system","Answer the user's questions based on the below context:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}")
    ])
    
    stuff_documents_chian = create_stuff_documents_chain(llm,prompt)
    
    return create_retrieval_chain(retriever_chain,stuff_documents_chian)

def get_response(user_input):
    
    
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)    
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })
    
    return response['answer']