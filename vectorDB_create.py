from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS

# ベクトルストア作成
def get_vectorstore(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents=chunks,embedding=embeddings)
    
    return vectorstore
