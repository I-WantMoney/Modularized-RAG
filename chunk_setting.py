from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
# チャンク設定
def get_chunks(full_doc):
    text_splitter1 = CharacterTextSplitter(
        separator = "\n| |\n\n",
        chunk_size = 1000,
        chunk_overlap = 10,
        length_function = len
    )
    
    temp_chunks = text_splitter1.split_documents(full_doc)
    
    text_splitter2 = CharacterTextSplitter(
        chunk_size = 8000,
        chunk_overlap = 10,
        length_function=len
    )
    chunks=[]
    # 文書が極めて長い場合の処理
    for doc in temp_chunks:
        if len(doc.page_content)>8000:
            split_docs = text_splitter2.split_text(doc.page_content)
            chunks.extend([Document(page_content=d) for d in split_docs])
        else:
            chunks.append(doc)
    return chunks
