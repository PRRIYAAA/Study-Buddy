import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    TextLoader
)

UPLOAD_DIR = "data/uploads"

def save_uploaded_file(uploaded_file, user_id):
    """
    Save uploaded file to disk under user's folder.
    Returns the saved file path.
    """
    # Create user-specific folder
    user_folder = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    # Save file
    file_path = os.path.join(user_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def load_document(file_path):
    """
    Extract text from document based on file type.
    Returns list of LangChain Document objects.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)

    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)

    elif ext == ".pptx":
        loader = UnstructuredPowerPointLoader(file_path)

    elif ext == ".txt":
        loader = TextLoader(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    documents = loader.load()
    return documents


def get_user_documents(user_id):
    """
    List all uploaded files for a user.
    """
    user_folder = os.path.join(UPLOAD_DIR, str(user_id))

    if not os.path.exists(user_folder):
        return []

    files = os.listdir(user_folder)
    return files