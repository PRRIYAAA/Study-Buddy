import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from rag.vectorstore import load_vectorstore, retrieve_relevant_documents, format_retrieved_context
from tools.tavily_tool import search_web
from memory.summary_memory import get_summary

load_dotenv()

MODEL_NAME = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

import time


def load_system_prompt():
    with open("prompts/system_prompt.txt", "r") as f:
        return f.read()


def safe_chat_completion(model, messages, max_tokens, retries=2):
    for attempt in range(retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
        except Exception as e:
            error_text = str(e).lower()
            if attempt < retries - 1 and ("429" in error_text or "too_many_requests" in error_text or "queue_exceeded" in error_text):
                time.sleep(1 * (2 ** attempt))
                continue
            raise


def extract_response_text(response):
    if not hasattr(response, 'choices') or not response.choices:
        return None

    choice = response.choices[0]
    if not hasattr(choice, 'message') or choice.message is None:
        return None

    content = getattr(choice.message, 'content', None)
    if content is None:
        return None

    return content


def needs_web_search(question, rag_context):
    """
    Ask LLM: is the RAG context enough to answer this question?
    Returns True if web search is needed.
    """
    check_prompt = f"""
You are a routing assistant.

A student asked: "{question}"

The following context was retrieved from their study documents:
{rag_context[:1800]}

Question: Is this context sufficient to answer the student's question?
Reply with only one word: YES or NO.
- YES if the context contains relevant information
- NO if the context is empty, unrelated, too vague, or the question needs latest/current information
"""
    try:
        response = safe_chat_completion(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": check_prompt}],
            max_tokens=10
        )
    except Exception as e:
        # If the router check fails, continue with document context if available.
        if rag_context:
            return False
        raise RuntimeError(
            f"Cerebras model request failed for model '{MODEL_NAME}' while checking whether web search is needed. "
            "Verify the model name and your account access. "
            f"Original error: {e}"
        ) from e

    answer_text = extract_response_text(response)
    if not answer_text:
        return False

    answer = answer_text.strip().upper()
    return "NO" in answer


def ask_question(question, user_id):
    """
    Full pipeline:
    1. Try RAG first
    2. If not enough → use Tavily web search
    3. Send context to LLM
    4. Return answer
    """

    system_prompt = load_system_prompt()
    context = ""
    source_used = ""

    # Get memory summary
    memory_summary = get_summary(user_id)

    # Try RAG
    db = load_vectorstore(user_id)
    if db:
        retrieved_docs = retrieve_relevant_documents(db, question, k=5)
        context = format_retrieved_context(retrieved_docs)

    # Decide source
    if not context or needs_web_search(question, context):
        context = search_web(question)
        source_used = "🌐 Web Search"
    else:
        source_used = "📄 Your Documents"

    # Build prompt with memory
    user_message = f"""
Student's Learning History (Memory):
{memory_summary if memory_summary else "No previous study history."}

---

Context ({source_used}):
{context}

---

Student Question:
{question}

Answer based on the provided context only.
If the context does not contain enough information, say that clearly and do not invent details.
Use memory only to personalize the explanation style, not as a factual source.
"""

    try:
        response = safe_chat_completion(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1024
        )
    except Exception as e:
        raise RuntimeError(
            f"Cerebras model request failed for model '{MODEL_NAME}'. "
            "Verify the model name and your account access. "
            f"Original error: {e}"
        ) from e

    answer_text = extract_response_text(response)
    if not answer_text:
        raise RuntimeError(
            "Cerebras response did not contain an answer. "
            "Check your model configuration and API access."
        )

    return answer_text.strip(), source_used
