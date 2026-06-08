try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError as err:
    HuggingFaceEmbeddings = None
    _huggingface_import_error = err


def get_embedding_model():
    """
    Load the sentence transformer embedding model.
    Downloads once, cached locally after that.
    """

    if HuggingFaceEmbeddings is None:
        raise ImportError(
            "The langchain_huggingface package is required to load embeddings. "
            "Install it with `pip install langchain-huggingface` and ensure you are using the project's venv. "
            f"Original error: {_huggingface_import_error}"
        )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    return embeddings


def needs_web_search(question, context):
    """
    Determine if web search is needed.
    """
    # Example logic: if the question is about a specific person or place, we need to search the web
    if "person" in question.lower() or "place" in question.lower():
        return True
    return False


def search_web(question):
    """
    Perform a web search.
    """
    # Example logic: use Google search
    return "https://www.google.com/search?q=" + question


def get_context(question, context):
    """
    Get the context for the question.
    """
    if not context or needs_web_search(question, context):
        context = search_web(question)
        source_used = "🌐 Web Search"
    else:
        source_used = "📄 Your Documents"
    return context, source_used