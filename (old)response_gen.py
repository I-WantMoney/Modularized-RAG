import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv

# new--------------------------------
# from langchain_community.chat_models import BedrockChat
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# llm = BedrockChat(
#     credentials_profile_name="https://047403811176.signin.aws.amazon.com/console",
#     model_id="anthropic.claude-3-sonnet-20240229-v1:0",
#     streaming=True,
#     callbacks=[StreamingStdOutCallbackHandler()],
# )
# -------------------------------------

load_dotenv()
llm_model = os.environ["OPENAI_API_MODEL"]

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI(model=llm_model,max_tokens = 4096) # カッコ内でapi-keyの指定、モデルの指定などができます。コードの先頭にdotenvを使ったので、自動的に.envファイルからapi-keyを取得します
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    # new---------------------------------
    contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
    )
    # ------------------------------------
    prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}"),
        ("user","Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    
    retriever_chain = create_history_aware_retriever(llm,retriever,prompt)
    
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    
    llm = ChatOpenAI(model=llm_model,max_tokens = 4096) # カッコ内でapi-keyの指定、モデルの指定などができます。コードの先頭にdotenvを使ったので、自動的に.envファイルからapi-keyを取得します
    # new-----------------------------------------
    system_prompt = (
        "You are an assistant for question-answering tasks."
        "Be awared that you have already said 'Hello, I am a bot' at first."
        "If you don't know the answer, just that say you don't know."
        "Your answer should be based on the below context:\n\n{context}"
    )
    # --------------------------------------------
    prompt = ChatPromptTemplate.from_messages([
        ("system",system_prompt),
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

    print(f"Full response: {response}")
    return response