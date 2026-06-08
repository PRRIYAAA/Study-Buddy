import sqlite3
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()

DB_PATH = "studybuddy.db"
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

def get_summary(user_id):
    """Get existing conversation summary for user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT summary FROM chat_summary WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""


def update_summary(user_id, new_question, new_answer):
    """
    After each chat, summarize what the student has learned.
    Store/update in DB.
    """
    existing_summary = get_summary(user_id)

    prompt = f"""
You are a memory manager for a study assistant.

Previous summary of what the student has studied:
{existing_summary if existing_summary else "No previous history."}

New conversation:
Student asked: {new_question}
Assistant answered: {new_answer[:500]}

Update the summary to include the new topic studied.
Keep it concise (max 200 words).
Focus on: topics covered, concepts learned, difficulty level observed.
"""

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    new_summary = response.choices[0].message.content.strip()

    # Save to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_summary (user_id, summary, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            summary = excluded.summary,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, new_summary))
    conn.commit()
    conn.close()


def save_chat_to_history(user_id, question, answer):
    """Save individual Q&A to chat_history table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, question, answer) VALUES (?, ?, ?)",
        (user_id, question, answer)
    )
    conn.commit()
    conn.close()


def get_recent_history(user_id, limit=5):
    """Get last N chats for this user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT question, answer FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    results = cursor.fetchall()
    conn.close()
    return list(reversed(results))