import os
from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embedding_model
from rag.chunker import split_documents

VECTOR_DB_DIR = "vector_db"
DEFAULT_RETRIEVAL_K = 5
DEFAULT_FETCH_K = 20


def _format_doc_source(doc):
    source_name = doc.metadata.get("source_name") or os.path.basename(doc.metadata.get("source", "Uploaded notes"))
    page = doc.metadata.get("page")
    chunk = doc.metadata.get("chunk")

    parts = [source_name]
    if page is not None:
        parts.append(f"page {page + 1}")
    if chunk is not None:
        parts.append(f"chunk {chunk}")

    return ", ".join(parts)


def retrieve_relevant_documents(db, query, k=DEFAULT_RETRIEVAL_K, fetch_k=DEFAULT_FETCH_K):
    """
    Return diverse, relevant chunks with source labels.
    MMR reduces repeated neighboring chunks that can crowd out better context.
    """
    if not db:
        return []

    try:
        docs = db.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=0.55,
        )
    except Exception:
        docs = db.similarity_search(query, k=k)

    return docs


def format_retrieved_context(docs):
    if not docs:
        return ""

    return "\n\n---\n\n".join(
        f"Source {i}: {_format_doc_source(doc)}\n{doc.page_content.strip()}"
        for i, doc in enumerate(docs, start=1)
        if doc.page_content and doc.page_content.strip()
    )

def build_vectorstore(documents, user_id):
    """
    Take raw documents, chunk them, embed them,
    and save to FAISS index for this user.
    """

    # Step 1: Chunk
    chunks = split_documents(documents)

    # Step 2: Load embedding model
    embeddings = get_embedding_model()

    # Step 3: Create FAISS index from chunks
    db = FAISS.from_documents(chunks, embeddings)

    # Step 4: Save to disk (user-specific folder)
    user_index_path = os.path.join(VECTOR_DB_DIR, str(user_id))
    os.makedirs(user_index_path, exist_ok=True)
    db.save_local(user_index_path)

    print(f"Vector store saved for user {user_id}")

    return db


def load_vectorstore(user_id):
    """
    Load existing FAISS index for a user.
    Returns None if no index exists yet.
    """

    user_index_path = os.path.join(VECTOR_DB_DIR, str(user_id))

    if not os.path.exists(user_index_path):
        return None

    embeddings = get_embedding_model()

    db = FAISS.load_local(
        user_index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db


def add_to_vectorstore(new_documents, user_id):
    """
    Add new documents to existing FAISS index.
    If no index exists, create a new one.
    """

    existing_db = load_vectorstore(user_id)

    chunks = split_documents(new_documents)
    embeddings = get_embedding_model()

    if existing_db:
        # Merge new chunks into existing index
        existing_db.add_documents(chunks)

        user_index_path = os.path.join(VECTOR_DB_DIR, str(user_id))
        existing_db.save_local(user_index_path)

        print(f"Added {len(chunks)} chunks to existing index.")
        return existing_db

    else:
        # First document — create fresh index
        return build_vectorstore(new_documents, user_id)
