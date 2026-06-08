# StudyBuddy AI

StudyBuddy AI is an AI-powered personal learning assistant for students. It lets users upload study material, ask questions from their notes, generate quizzes, create flashcards, and keep a short memory of previous learning conversations.

The app is built with Streamlit, Cerebras LLM inference, LangChain, FAISS vector search, SentenceTransformers embeddings, Tavily web search, SQLite, and bcrypt authentication.

## Features

| Feature | Description |
|---|---|
| Document upload | Upload PDF, DOCX, PPTX, and TXT files |
| RAG question answering | Ask questions answered from uploaded notes |
| Web search fallback | Uses Tavily when uploaded notes do not contain enough context |
| Quiz generator | Creates interactive MCQ quizzes with scoring and explanations |
| Flashcards | Creates memorization cards from uploaded notes |
| Memory | Stores chat history and a conversation summary |
| Authentication | Login and register with bcrypt password hashing |
| Light and dark UI | Student-friendly interface with readable contrast in both modes |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit with custom HTML/CSS |
| LLM | Cerebras API, default model `gpt-oss-120b` |
| RAG | LangChain + FAISS |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Search | Tavily API |
| Database | SQLite |
| Authentication | bcrypt |

## Project Structure

```text
Study-Buddy/
├── app.py
├── requirements.txt
├── README.md
├── auth/
│   └── login.py
├── database/
│   └── db.py
├── rag/
│   ├── loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vectorstore.py
│   └── rag_chain.py
├── tools/
│   └── tavily_tool.py
├── memory/
│   └── summary_memory.py
├── prompts/
│   └── system_prompt.txt
├── quizzes/
│   └── quiz_generator.py
├── flashcards/
│   └── flashcard_generator.py
├── data/
│   └── uploads/
└── vector_db/
```

## How It Works

1. A student registers or logs in.
2. The student uploads notes as PDF, DOCX, PPTX, or TXT.
3. The loader extracts text from the file.
4. The chunker splits text into overlapping study-friendly chunks.
5. Chunks are embedded with MiniLM and stored in a per-user FAISS index.
6. When the student asks a question, the app retrieves relevant chunks with MMR search.
7. A router checks whether the notes contain enough context.
8. If notes are enough, the answer is generated from uploaded documents.
9. If notes are not enough, Tavily web search is used as fallback.
10. The answer is displayed, saved to chat history, and added to memory summary.

## RAG and Chunking Details

Current chunking uses:

```python
chunk_size = 850
chunk_overlap = 150
separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]
```

This keeps chunks smaller and more focused than large page-sized chunks. Each chunk stores metadata such as source file name, page number when available, and chunk number. Retrieval uses Max Marginal Relevance so repeated nearby chunks do not crowd out other useful sections.

## Database Schema

```text
users
  id, username, password, created_at

uploaded_documents
  id, user_id, filename, file_path, uploaded_at

chat_history
  id, user_id, question, answer, timestamp

chat_summary
  id, user_id, summary, updated_at
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env`

```env
CEREBRAS_API_KEY=your_cerebras_api_key
TAVILY_API_KEY=your_tavily_api_key
CEREBRAS_MODEL=gpt-oss-120b
```

### 3. Run the app

```bash
streamlit run app.py
```

## API Keys

| Service | Purpose | Link |
|---|---|---|
| Cerebras | LLM answers, quizzes, flashcards, memory summaries | https://cloud.cerebras.ai |
| Tavily | Web search fallback | https://tavily.com |

## Main Modules

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI, tabs, upload flow, chat, quiz, flashcards |
| `auth/login.py` | User registration and login |
| `database/db.py` | SQLite table creation and helper functions |
| `rag/loader.py` | Extracts text from uploaded documents |
| `rag/chunker.py` | Splits documents into chunks for embeddings |
| `rag/embeddings.py` | Loads HuggingFace embedding model |
| `rag/vectorstore.py` | Builds, loads, updates, and searches FAISS index |
| `rag/rag_chain.py` | RAG pipeline and web-search routing |
| `tools/tavily_tool.py` | Tavily web search integration |
| `quizzes/quiz_generator.py` | Generates MCQ quiz JSON from notes |
| `flashcards/flashcard_generator.py` | Generates flashcard JSON from notes |
| `memory/summary_memory.py` | Saves chat history and summary memory |

## Troubleshooting

| Problem | Fix |
|---|---|
| Text is invisible in dark mode | Use the updated CSS in `app.py`; avoid new hard-coded black or pale text colors |
| Answers contain wrong details | Re-upload/re-index notes after chunking changes and ask topics that exist in uploaded documents |
| Quiz or flashcards use weak context | The generator now raises an error when no relevant notes are found |
| FAISS load warning | The app uses LangChain FAISS local loading for a trusted local project index |
| API error | Check `.env`, model access, and API key limits |

## Development Notes

- Keep `.env`, `studybuddy.db`, `data/uploads/`, and `vector_db/` out of public commits if they contain private data.
- After changing chunking or embeddings, rebuild the FAISS index by uploading documents again or clearing the old `vector_db/<user_id>` folder.
- Prefer source-grounded answers. The prompt asks the model to say when context is insufficient instead of guessing.

## Built By

StudyBuddy AI, an academic learning assistant project built for AI-powered study support.
