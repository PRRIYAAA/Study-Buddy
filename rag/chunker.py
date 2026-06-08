from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 850
CHUNK_OVERLAP = 150


def split_documents(documents):
    """
    Split documents into smaller chunks.
    
    documents: list of LangChain Document objects (from loader.py)
    returns:   list of smaller Document chunks
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    for chunk_number, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk"] = chunk_number
        source = chunk.metadata.get("source")
        if source:
            chunk.metadata["source_name"] = source.split("/")[-1].split("\\")[-1]

    print(f"Total chunks created: {len(chunks)}")

    return chunks
