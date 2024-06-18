from langchain.text_splitter import CharacterTextSplitter

# チャンク設定
def get_chunks(full_doc):
    text_splitter = CharacterTextSplitter(
        separator = "\n| |\n\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len
    )
    
    chunks = text_splitter.split_documents(full_doc)
    
    return chunks