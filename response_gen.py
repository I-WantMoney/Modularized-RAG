import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
# new -----------------------------------------------
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
# ---------------------------------------------------
from dotenv import load_dotenv

# Bedrock Model------------------------
from langchain_aws import ChatBedrock

LLM = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)
# -------------------------------------

# # OpenAI Model -----------------------
# load_dotenv()
# llm_model = os.environ["OPENAI_API_MODEL"]
# LLM = ChatOpenAI(model=llm_model) # カッコ内でapi-keyの指定、モデルの指定などができます。コードの先頭にdotenvを使ったので、自動的に.envファイルからapi-keyを取得します
# # ------------------------------------

# new --------------------------------
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]
# ------------------------------------

def get_context_retriever_chain(vector_store):
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    # new---------------------------------
    contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
    "And be aware that you have already said 'Hello, I am a bot' at first no matter whether this is recorded in chat history."
    )
    # ------------------------------------
    prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}"),
        ("user","Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    
    retriever_chain = create_history_aware_retriever(LLM,retriever,prompt)
    
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    
    system_prompt = (
        "You are a kind assistant for question-answering tasks."
        "Given below context:\n\n{context}"
        "You should try to find answers base on the context."
        "Answer user questions concisely."
        "If you don't know the answer, just that say you didn't find it from the context,"
        "but as long as you know the answer, you can say it even if it is not from the context,"
        "just be sure to mark where the answer is from, your knowledge, or chat history, or the context."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}")
    ])
    
    stuff_documents_chian = create_stuff_documents_chain(LLM,prompt)
    
    return create_retrieval_chain(retriever_chain,stuff_documents_chian)

# RAGありの回答生成
def rag_get_response(user_input):
     
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)    
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    new_rag = RunnableWithMessageHistory(
        conversation_rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    response = new_rag.invoke(
        {"input": user_input,},
        config={
            "configurable": {"session_id": st.session_state.session_id}
        }
        )
    print(f"Full response: {response}")
    
    return response

# RAG抜きの回答生成
def qa_get_response(user_input):
    
    system_prompt = (
        "You are a kind assistant. "
        "Answer user questions concisely." 
        "And be aware that you have already said 'Hello, I am a bot' at first no matter whether this is recorded in chat history."
    )
    
    # プロンプトテンプレートの作成
    simple_qa_prompt = ChatPromptTemplate.from_messages([
        ("system",system_prompt ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    qa_chain = simple_qa_prompt | LLM
    
    simple_qa_with_history = RunnableWithMessageHistory(
        qa_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )
    
    response = simple_qa_with_history.invoke(
        {"input": user_input},
        config={
            "configurable": {"session_id": st.session_state.session_id}
            }
        )
    print(f"Full response: {response}")
    return response