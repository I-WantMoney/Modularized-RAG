from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma

# ベクトルストア生成
def get_vectorstore(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents=chunks,embedding=embeddings)
    
    return vectorstore