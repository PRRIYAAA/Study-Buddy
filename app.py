import streamlit as st
import os
from database.db import create_database, save_document_record, get_user_document_records
from auth.login import register_user, login_user
from rag.loader import save_uploaded_file, load_document
from rag.vectorstore import add_to_vectorstore, load_vectorstore
from rag.rag_chain import ask_question
from memory.summary_memory import update_summary, save_chat_to_history, get_summary
from quizzes.quiz_generator import generate_quiz
from flashcards.flashcard_generator import generate_flashcards

create_database()

st.set_page_config(
    page_title="StudyBuddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

:root {
    color-scheme: light;
    --sb-bg: #f8fafc;
    --sb-surface: #ffffff;
    --sb-surface-soft: #eef2ff;
    --sb-surface-muted: #f1f5f9;
    --sb-text: #111827;
    --sb-text-soft: #475569;
    --sb-text-muted: #64748b;
    --sb-border: #dbe3f0;
    --sb-primary: #4f46e5;
    --sb-primary-strong: #3730a3;
    --sb-primary-soft: #eef2ff;
    --sb-pink: #be185d;
    --sb-green: #15803d;
    --sb-blue: #1d4ed8;
    --sb-amber: #a16207;
    --sb-orange: #c2410c;
    --sb-danger: #be123c;
    --sb-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
}

html, body, .stApp, [data-testid="stAppViewContainer"], .main {
    background: var(--sb-bg) !important;
    font-family: 'Nunito', sans-serif !important;
    color: var(--sb-text) !important;
}
[data-testid="stSidebar"] {
    background: var(--sb-surface) !important;
    border-right: 1px solid var(--sb-border) !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #0891b2) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 1.5rem !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: var(--sb-shadow) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px rgba(79,70,229,0.32) !important;
}

input, textarea, [data-testid="stTextInput"] input {
    background: var(--sb-surface) !important;
    border: 1.5px solid var(--sb-border) !important;
    border-radius: 12px !important;
    color: var(--sb-text) !important;
    font-family: 'Nunito', sans-serif !important;
}
input:focus, textarea:focus {
    border-color: var(--sb-primary) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.18) !important;
}

[data-testid="stFileUploader"] {
    background: var(--sb-surface-soft) !important;
    border: 2px dashed var(--sb-primary) !important;
    border-radius: 14px !important;
}
[data-testid="stChatMessage"] {
    background: var(--sb-surface) !important;
    border: 1.5px solid var(--sb-border) !important;
    border-radius: 16px !important;
    margin-bottom: 0.75rem !important;
    color: var(--sb-text) !important;
}
[data-testid="stExpander"] {
    background: var(--sb-surface) !important;
    border: 1.5px solid var(--sb-border) !important;
    border-radius: 14px !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: var(--sb-text-soft) !important;
    font-size: 1rem !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--sb-primary) !important;
    border-bottom-color: var(--sb-primary) !important;
}
hr { border-color: var(--sb-border) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--sb-bg); }
::-webkit-scrollbar-thumb { background: var(--sb-primary); border-radius: 99px; }

.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown div,
[data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"],
[data-testid="stChatMessage"] p {
    color: var(--sb-text) !important;
}

.stMarkdown small, .stCaptionContainer, .st-emotion-cache-1vbkxwb,
[style*="color:#6b7280"], [style*="color:#9ca3af"],
[style*="color: #6b7280"], [style*="color: #9ca3af"] {
    color: var(--sb-text-muted) !important;
}

[style*="background:#ffffff"], [style*="background: #ffffff"] {
    background: var(--sb-surface) !important;
}
[style*="background:#eef2ff"], [style*="background: #eef2ff"],
[style*="background:#f9fafb"], [style*="background: #f9fafb"] {
    background: var(--sb-surface-soft) !important;
}
[style*="background:#fdf2f8"], [style*="background: #fdf2f8"] {
    background: #fff1f7 !important;
}
[style*="background:#f0fdf4"], [style*="background: #f0fdf4"] {
    background: #ecfdf5 !important;
}
[style*="background:#fff7ed"], [style*="background: #fff7ed"] {
    background: #fff7ed !important;
}
[style*="background:#fefce8"], [style*="background: #fefce8"] {
    background: #fefce8 !important;
}
[style*="background:#eff6ff"], [style*="background: #eff6ff"] {
    background: #eff6ff !important;
}
[style*="border:2px solid #e0e7ff"], [style*="border:1.5px solid #e0e7ff"],
[style*="border:1.5px solid #c7d2fe"], [style*="border:2px dashed #c7d2fe"] {
    border-color: var(--sb-border) !important;
}
[style*="color:#1e1b4b"], [style*="color: #1e1b4b"],
[style*="color:#374151"], [style*="color: #374151"] {
    color: var(--sb-text) !important;
}
[style*="color:#4338ca"], [style*="color:#6366f1"],
[style*="color: #4338ca"], [style*="color: #6366f1"] {
    color: var(--sb-primary-strong) !important;
}
[style*="color:#be185d"], [style*="color: #be185d"],
[style*="color:#db2777"], [style*="color: #db2777"] {
    color: var(--sb-pink) !important;
}
[style*="color:#15803d"], [style*="color: #15803d"] {
    color: var(--sb-green) !important;
}
[style*="color:#1d4ed8"], [style*="color: #1d4ed8"] {
    color: var(--sb-blue) !important;
}
[style*="color:#a16207"], [style*="color: #a16207"] {
    color: var(--sb-amber) !important;
}
[style*="color:#c2410c"], [style*="color: #c2410c"] {
    color: var(--sb-orange) !important;
}
[data-testid="stSidebar"] {
    color: var(--sb-text) !important;
}
[style*="linear-gradient(135deg,#6366f1,#8b5cf6)"] *,
[style*="linear-gradient(135deg, #6366f1, #8b5cf6)"] * {
    color: #ffffff !important;
}

[data-testid="stChatInput"] {
    background: var(--sb-surface) !important;
    border: 1px solid var(--sb-border) !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--sb-text) !important;
    -webkit-text-fill-color: var(--sb-text) !important;
}

::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

@media (max-width: 720px) {
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    .stButton > button {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

for key, val in {
    "logged_in": False,
    "user_id": None,
    "username": None,
    "last_loaded_docs": None,
    "chat_history": [],
    "quiz_data": None,
    "quiz_answers": {},
    "quiz_submitted": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


def show_auth():
    st.markdown("""
    <div style="text-align:center; padding: 3rem 1rem 2rem;">
        <div style="display:inline-flex; align-items:center; gap:14px;
                    background:#ffffff; border:2px solid #e0e7ff; border-radius:24px;
                    padding:1rem 2rem; box-shadow:0 4px 24px rgba(99,102,241,0.12); margin-bottom:1.5rem;">
            <span style="font-size:2.5rem;">🎓</span>
            <div style="text-align:left;">
                <div style="font-family:'Nunito',sans-serif; font-size:2rem; font-weight:900; color:#4338ca; line-height:1.1;">
                    StudyBuddy AI
                </div>
                <div style="color:#6b7280; font-size:0.9rem; font-weight:600;">Your personal AI learning assistant</div>
            </div>
        </div>
        <p style="color:#6b7280; font-size:1rem; margin:0;">Upload notes · Ask questions · Generate quizzes · Create flashcards</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="Your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login", key="login_btn", use_container_width=True):
                if username and password:
                    success, result = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_id = result
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.warning("Fill in both fields.")
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            new_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
            new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Choose a password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", key="reg_btn", use_container_width=True):
                if new_user and new_pass:
                    success, msg = register_user(new_user, new_pass)
                    if success:
                        st.success(msg + " Please login.")
                    else:
                        st.error(msg)
                else:
                    st.warning("Fill in both fields.")

    st.markdown("""
    <div style="display:flex; gap:0.6rem; justify-content:center; flex-wrap:wrap; margin-top:2rem;">
        <span style="background:#eef2ff; color:#4338ca; border:1.5px solid #c7d2fe; border-radius:50px; padding:0.35rem 1rem; font-size:0.82rem; font-weight:700;">📄 RAG Documents</span>
        <span style="background:#fdf2f8; color:#be185d; border:1.5px solid #fbcfe8; border-radius:50px; padding:0.35rem 1rem; font-size:0.82rem; font-weight:700;">🌐 Web Search</span>
        <span style="background:#f0fdf4; color:#15803d; border:1.5px solid #bbf7d0; border-radius:50px; padding:0.35rem 1rem; font-size:0.82rem; font-weight:700;">🧠 Quiz Generator</span>
        <span style="background:#fff7ed; color:#c2410c; border:1.5px solid #fed7aa; border-radius:50px; padding:0.35rem 1rem; font-size:0.82rem; font-weight:700;">🃏 Flashcards</span>
        <span style="background:#fefce8; color:#a16207; border:1.5px solid #fde68a; border-radius:50px; padding:0.35rem 1rem; font-size:0.82rem; font-weight:700;">💾 Memory</span>
    </div>
    """, unsafe_allow_html=True)


def show_dashboard():
    with st.sidebar:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6); border-radius:16px;
                    padding:1rem 1.2rem; margin-bottom:1rem;">
            <div style="font-size:1.8rem;">🎓</div>
            <div style="font-size:1.05rem; font-weight:900; color:#fff; margin-top:0.2rem;">{st.session_state.username}</div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.75);">StudyBuddy AI</div>
        </div>
        """, unsafe_allow_html=True)

        summary = get_summary(st.session_state.user_id)
        if summary:
            with st.expander("🧠 My Learning Memory"):
                st.write(summary)

        st.markdown("---")
        st.markdown("**📂 Upload Study Material**")
        uploaded_file = st.file_uploader("PDF, DOCX, PPTX, TXT", type=["pdf","docx","pptx","txt"], label_visibility="collapsed")

        if uploaded_file is not None:
            if st.button("⚡ Process Document", use_container_width=True):
                with st.spinner("Indexing..."):
                    try:
                        file_path = save_uploaded_file(uploaded_file, st.session_state.user_id)
                        documents = load_document(file_path)
                        save_document_record(st.session_state.user_id, uploaded_file.name, file_path)
                        add_to_vectorstore(documents, st.session_state.user_id)
                        st.session_state.last_loaded_docs = documents
                        st.success(f"✅ Done! {len(documents)} pages indexed")
                    except Exception as e:
                        st.error(f"❌ {e}")
                        st.exception(e)

        st.markdown("---")
        st.markdown("**📁 Your Documents**")
        records = get_user_document_records(st.session_state.user_id)
        if records:
            for filename, _ in records:
                st.markdown(f"""
                <div style="background:#eef2ff; border:1.5px solid #c7d2fe; border-radius:10px;
                            padding:0.45rem 0.8rem; margin-bottom:0.4rem; font-size:0.82rem;
                            color:#3730a3; font-weight:600;">📄 {filename}</div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No documents uploaded yet.")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k, v in {"logged_in":False,"user_id":None,"username":None,"last_loaded_docs":None,
                         "chat_history":[],"quiz_data":None,"quiz_answers":{},"quiz_submitted":False}.items():
                st.session_state[k] = v
            st.rerun()

    # HEADER
    st.markdown("""
    <div style="padding:1.2rem 0 0.8rem; display:flex; align-items:center; gap:14px;">
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6); border-radius:16px;
                    padding:0.7rem 0.9rem; font-size:1.8rem; box-shadow:0 4px 16px rgba(99,102,241,0.3);">🎓</div>
        <div>
            <div style="font-family:'Nunito',sans-serif; font-size:1.9rem; font-weight:900; color:#1e1b4b; line-height:1.1;">
                StudyBuddy AI
            </div>
            <div style="color:#6b7280; font-size:0.88rem; font-weight:600;">
                Ask questions · Generate quizzes · Create flashcards
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # STATS
    doc_count = len(get_user_document_records(st.session_state.user_id))
    chat_count = len(st.session_state.chat_history) // 2
    has_mem = "Active" if get_summary(st.session_state.user_id) else "Empty"
    mc = "#15803d" if has_mem == "Active" else "#9ca3af"
    mb = "#f0fdf4" if has_mem == "Active" else "#f9fafb"
    mbd = "#bbf7d0" if has_mem == "Active" else "#e5e7eb"

    st.markdown(f"""
    <div style="display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap;">
        <div style="background:#eef2ff; border:1.5px solid #c7d2fe; border-radius:14px;
                    padding:0.8rem 1.4rem; flex:1; min-width:120px; text-align:center;">
            <div style="font-size:1.6rem; font-weight:900; color:#4338ca;">{doc_count}</div>
            <div style="font-size:0.75rem; color:#6366f1; font-weight:700;">Documents</div>
        </div>
        <div style="background:#fdf2f8; border:1.5px solid #fbcfe8; border-radius:14px;
                    padding:0.8rem 1.4rem; flex:1; min-width:120px; text-align:center;">
            <div style="font-size:1.6rem; font-weight:900; color:#be185d;">{chat_count}</div>
            <div style="font-size:0.75rem; color:#db2777; font-weight:700;">Questions Asked</div>
        </div>
        <div style="background:{mb}; border:1.5px solid {mbd}; border-radius:14px;
                    padding:0.8rem 1.4rem; flex:1; min-width:120px; text-align:center;">
            <div style="font-size:1.6rem; font-weight:900; color:{mc};">{has_mem}</div>
            <div style="font-size:0.75rem; color:{mc}; font-weight:700;">Memory</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_chat, tab_quiz, tab_flash = st.tabs(["💬  Chat", "🧠  Quiz Generator", "🃏  Flashcards"])

    # CHAT
    with tab_chat:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align:center; padding:2.5rem 1rem; background:#ffffff;
                        border:2px dashed #c7d2fe; border-radius:16px; margin-bottom:1rem;">
                <div style="font-size:2.5rem;">💬</div>
                <div style="color:#6366f1; font-weight:800; font-size:1.05rem; margin-top:0.4rem;">Start a conversation!</div>
                <div style="color:#9ca3af; font-size:0.88rem; margin-top:0.3rem;">
                    Try: "Explain OSI Model" · "Summarize Unit 3" · "What is normalization?"
                </div>
            </div>
            """, unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if "source" in msg:
                    sc = "#15803d" if "Documents" in msg["source"] else "#1d4ed8"
                    sb = "#f0fdf4" if "Documents" in msg["source"] else "#eff6ff"
                    st.markdown(f'<span style="background:{sb}; color:{sc}; border-radius:50px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:700;">{msg["source"]}</span>', unsafe_allow_html=True)

        question = st.chat_input("Ask anything from your notes...")
        if question:
            with st.chat_message("user"):
                st.write(question)
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer, source = ask_question(question, st.session_state.user_id)
                    st.write(answer)
                    sc = "#15803d" if "Documents" in source else "#1d4ed8"
                    sb = "#f0fdf4" if "Documents" in source else "#eff6ff"
                    st.markdown(f'<span style="background:{sb}; color:{sc}; border-radius:50px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:700;">{source}</span>', unsafe_allow_html=True)
            st.session_state.chat_history.append({"role":"assistant","content":answer,"source":source})
            save_chat_to_history(st.session_state.user_id, question, answer)
            update_summary(st.session_state.user_id, question, answer)

    # QUIZ
    with tab_quiz:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#eef2ff,#fdf2f8); border:1.5px solid #c7d2fe;
                    border-radius:16px; padding:1.2rem 1.5rem; margin-bottom:1.5rem;">
            <div style="font-size:1.1rem; font-weight:900; color:#4338ca;">🧠 Interactive Quiz Generator</div>
            <div style="color:#6b7280; font-size:0.85rem; margin-top:0.2rem;">Click your answer · See instant feedback · Check explanations</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2.5, 1])
        with col1:
            quiz_topic = st.text_input("Topic", placeholder="e.g. OSI Model, SQL Joins, Linked Lists...", key="quiz_topic")
        with col2:
            num_q = st.slider("Questions", 3, 10, 5, key="num_q")

        gc, rc = st.columns(2)
        with gc:
            if st.button("🎯 Generate Quiz", key="gen_quiz", use_container_width=True):
                if quiz_topic:
                    with st.spinner("Generating your quiz..."):
                        try:
                            questions = generate_quiz(quiz_topic, st.session_state.user_id, num_q)
                            st.session_state.quiz_data = questions
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_submitted = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Enter a topic first!")
        with rc:
            if st.session_state.quiz_data and st.button("🔄 Reset", key="reset_quiz", use_container_width=True):
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()

        if st.session_state.quiz_data:
            questions = st.session_state.quiz_data
            total = len(questions)

            st.markdown(f"""
            <div style="background:#eef2ff; border:1.5px solid #c7d2fe; border-radius:12px;
                        padding:0.6rem 1.2rem; margin-bottom:1.2rem; color:#4338ca; font-weight:700; font-size:0.9rem;">
                {total} Questions · Click Select next to an option · Submit when ready
            </div>
            """, unsafe_allow_html=True)

            for i, q in enumerate(questions):
                answered = i in st.session_state.quiz_answers
                selected = st.session_state.quiz_answers.get(i)
                correct_letter = q["answer"].strip()[0].upper()

                st.markdown(f"""
                <div style="background:#ffffff; border:1.5px solid #e0e7ff; border-radius:16px;
                            padding:1.2rem 1.4rem; margin-bottom:0.5rem;">
                    <div style="font-weight:800; color:#1e1b4b; font-size:1rem; margin-bottom:0.8rem;">
                        Q{i+1}. {q['question']}
                    </div>
                """, unsafe_allow_html=True)

                for opt in q["options"]:
                    opt_letter = opt.strip()[0].upper()
                    if st.session_state.quiz_submitted and answered:
                        if opt_letter == correct_letter:
                            bg, border, color = "#f0fdf4", "#86efac", "#15803d"
                        elif opt_letter == selected:
                            bg, border, color = "#fff1f2", "#fca5a5", "#be123c"
                        else:
                            bg, border, color = "#f9fafb", "#e5e7eb", "#6b7280"
                    elif answered and opt_letter == selected:
                        bg, border, color = "#eef2ff", "#818cf8", "#4338ca"
                    else:
                        bg, border, color = "#f9fafb", "#e5e7eb", "#374151"

                    opt_col, btn_col = st.columns([8, 1])
                    with opt_col:
                        st.markdown(f"""
                        <div style="background:{bg}; border:2px solid {border}; border-radius:12px;
                                    padding:0.6rem 1rem; color:{color}; font-weight:700;
                                    font-size:0.9rem; margin-bottom:0.3rem;">{opt}</div>
                        """, unsafe_allow_html=True)
                    with btn_col:
                        if not st.session_state.quiz_submitted:
                            if st.button("Select", key=f"q{i}_{opt_letter}"):
                                st.session_state.quiz_answers[i] = opt_letter
                                st.rerun()

                if st.session_state.quiz_submitted and answered:
                    if selected == correct_letter:
                        st.markdown(f'<div style="background:#f0fdf4; border-left:4px solid #22c55e; border-radius:0 10px 10px 0; padding:0.6rem 1rem; color:#15803d; font-size:0.85rem; margin-top:0.3rem; margin-bottom:0.5rem;">✅ Correct! 💡 {q["explanation"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="background:#eff6ff; border-left:4px solid #3b82f6; border-radius:0 10px 10px 0; padding:0.6rem 1rem; color:#1d4ed8; font-size:0.85rem; margin-top:0.3rem; margin-bottom:0.5rem;">✅ Correct: <b>{correct_letter}</b> · 💡 {q["explanation"]}</div>', unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

            answered_count = len(st.session_state.quiz_answers)
            if not st.session_state.quiz_submitted:
                st.markdown(f"<p style='color:#6b7280; font-size:0.85rem;'>{answered_count}/{total} answered</p>", unsafe_allow_html=True)
                if st.button("📝 Submit Quiz", key="submit_quiz", use_container_width=True):
                    if answered_count == total:
                        st.session_state.quiz_submitted = True
                        st.rerun()
                    else:
                        st.warning(f"Answer all {total} questions! ({answered_count}/{total} done)")
            else:
                score = sum(1 for i, q in enumerate(questions)
                            if st.session_state.quiz_answers.get(i) == q["answer"].strip()[0].upper())
                pct = int((score / total) * 100)
                if pct >= 80:
                    sc, sb, sm = "#15803d", "#f0fdf4", "🎉 Excellent!"
                elif pct >= 60:
                    sc, sb, sm = "#a16207", "#fefce8", "👍 Good job!"
                else:
                    sc, sb, sm = "#be123c", "#fff1f2", "📚 Keep studying!"
                st.markdown(f"""
                <div style="background:{sb}; border-radius:16px; padding:1.5rem; text-align:center; margin-top:1rem;">
                    <div style="font-size:2.5rem; font-weight:900; color:{sc};">{score}/{total}</div>
                    <div style="font-size:1.1rem; font-weight:800; color:{sc};">{pct}% · {sm}</div>
                </div>
                """, unsafe_allow_html=True)

    # FLASHCARDS
    with tab_flash:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#f0fdf4,#fefce8); border:1.5px solid #bbf7d0;
                    border-radius:16px; padding:1.2rem 1.5rem; margin-bottom:1.5rem;">
            <div style="font-size:1.1rem; font-weight:900; color:#15803d;">🃏 Flashcard Generator</div>
            <div style="color:#6b7280; font-size:0.85rem; margin-top:0.2rem;">Perfect for quick revision and memorization</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2.5, 1])
        with col1:
            flash_topic = st.text_input("Topic", placeholder="e.g. TCP/IP, DBMS Concepts, Sorting Algorithms...", key="flash_topic")
        with col2:
            num_cards = st.slider("Cards", 5, 15, 10, key="num_cards")

        if st.button("✨ Generate Flashcards", key="gen_flash", use_container_width=True):
            if flash_topic:
                with st.spinner("Creating flashcards..."):
                    try:
                        cards = generate_flashcards(flash_topic, st.session_state.user_id, num_cards)
                        st.markdown(f'<div style="background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:0.6rem 1.2rem; margin-bottom:1rem; color:#15803d; font-weight:700; font-size:0.9rem;">✅ {len(cards)} flashcards created for "{flash_topic}"</div>', unsafe_allow_html=True)
                        card_colors = [
                            ("#eef2ff","#c7d2fe","#4338ca"),
                            ("#fdf2f8","#fbcfe8","#be185d"),
                            ("#f0fdf4","#bbf7d0","#15803d"),
                            ("#fff7ed","#fed7aa","#c2410c"),
                            ("#fefce8","#fde68a","#a16207"),
                            ("#eff6ff","#bfdbfe","#1d4ed8"),
                        ]
                        cols = st.columns(2)
                        for i, card_data in enumerate(cards):
                            bg, border, tc = card_colors[i % len(card_colors)]
                            with cols[i % 2]:
                                with st.expander(f"Card {i+1}: {card_data['front']}"):
                                    st.markdown(f'<div style="background:{bg}; border-left:4px solid {border}; border-radius:0 12px 12px 0; padding:0.8rem 1rem; color:{tc}; font-size:0.92rem; font-weight:600; line-height:1.6;">{card_data["back"]}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Flashcard error: {e}")
            else:
                st.warning("Enter a topic first!")


if st.session_state.logged_in:
    show_dashboard()
else:
    show_auth()
