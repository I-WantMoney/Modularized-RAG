from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

# ベクトルストア作成
def get_vectorstore(chunks):
    
    # # OpenAI Model ----------------
    # embeddings = OpenAIEmbeddings()
    # # -----------------------------
    
    # Bedrock Model ---------------
    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1",
        region_name="us-east-1"
    )
    # -----------------------------

    vectorstore = FAISS.from_documents(documents=chunks,embedding=embeddings)
    
    return vectorstore
