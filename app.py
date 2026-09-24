"""
app.py
Main Streamlit application for the Study Tutor Agent.
"""

import os
import streamlit as st

from tutor_agent import ask_tutor
from pdf_utils import process_pdf, get_relevant_chunks
from session_utils import (
    init_session_state,
    add_message,
    get_chat_history_text,
    reset_pdf,
    new_session,
)

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="Study Tutor Agent",
    page_icon="📘",
    layout="wide",
)

# ---------- Custom CSS: Dark theme with neon blue/cyan accents ----------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #e6e6e6;
    }

    h1, h2, h3 {
        color: #00e5ff;
    }

    .main-header {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
    }

    .main-header h1 {
        font-size: 2.5rem;
        color: #00e5ff;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
        margin-bottom: 0;
    }

    .main-header p {
        color: #9fa8b5;
        font-size: 1.1rem;
        margin-top: 0.3rem;
    }

    .stButton > button {
        background-color: #00e5ff;
        color: #0e1117;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: 0.2s;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #00b8cc;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #12161f;
        border-right: 1px solid #1f2937;
    }

    .stChatMessage {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Initialize Session State ----------
init_session_state()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Study Mode")

    study_mode = st.radio(
        "Choose how you want to study:",
        options=["General Study", "Ask from PDF"],
        index=0 if st.session_state.study_mode == "General Study" else 1,
    )
    st.session_state.study_mode = study_mode

    st.markdown("---")

    if study_mode == "Ask from PDF":
        st.markdown("### 📄 Upload PDF")
        uploaded_file = st.file_uploader("Upload one PDF file", type=["pdf"])

        if uploaded_file is not None:
            if st.session_state.pdf_name != uploaded_file.name:
                with st.spinner("Reading and processing PDF..."):
                    chunks = process_pdf(uploaded_file)

                if len(chunks) == 0:
                    st.error(
                        "Could not extract any text from this PDF. "
                        "It may be empty, scanned as an image, or corrupted."
                    )
                else:
                    st.session_state.pdf_chunks = chunks
                    st.session_state.pdf_name = uploaded_file.name
                    st.success(f"Loaded: {uploaded_file.name}")

        if st.session_state.pdf_name:
            st.info(f"📎 Active PDF: **{st.session_state.pdf_name}**")
            if st.button("🗑️ Remove PDF"):
                reset_pdf()
                st.rerun()
        else:
            st.warning("No PDF uploaded yet.")

    st.markdown("---")

    if st.button("🔄 Clear Chat / New Session"):
        new_session()
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(
        "**Study Tutor Agent** is an AI-powered study assistant. "
        "Ask general academic questions, or upload a PDF to ask "
        "questions about that specific document."
    )

# ---------- Header ----------
st.markdown(
    """
    <div class="main-header">
        <h1>📘 Study Tutor Agent</h1>
        <p>Your AI-powered personal study assistant</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Welcome Message ----------
if len(st.session_state.messages) == 0:
    st.markdown(
        """
        👋 **Welcome!** I'm your Study Tutor Agent.

        - Ask me any academic question in **General Study** mode.
        - Or switch to **Ask from PDF** mode and upload a document to
          ask questions about that specific document.

        **Example questions:**
        - "Explain Newton's second law of motion with an example."
        - "What is the difference between mitosis and meiosis?"
        - "Summarize the main argument in this PDF."
        """
    )

# ---------- Display Chat History ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Chat Input ----------
user_question = st.chat_input("Ask your study question here...")

if user_question:
    if user_question.strip() == "":
        st.warning("Please enter a valid question.")
    else:
        # Show the user's message immediately
        add_message("user", user_question)
        with st.chat_message("user"):
            st.markdown(user_question)

        # Check API key before calling the agent
        if not os.environ.get("GROQ_API_KEY"):
            error_msg = (
                "⚠️ GROQ_API_KEY is not configured. Please add it to your "
                "Streamlit Secrets to use the Study Tutor Agent."
            )
            add_message("assistant", error_msg)
            with st.chat_message("assistant"):
                st.markdown(error_msg)
        else:
            chat_history_text = get_chat_history_text()
            pdf_context = None

            # Build PDF context if in "Ask from PDF" mode
            if st.session_state.study_mode == "Ask from PDF":
                if not st.session_state.pdf_chunks:
                    warning_msg = (
                        "⚠️ You're in **Ask from PDF** mode, but no PDF has been "
                        "uploaded yet. Please upload a PDF in the sidebar, or "
                        "switch to **General Study** mode."
                    )
                    add_message("assistant", warning_msg)
                    with st.chat_message("assistant"):
                        st.markdown(warning_msg)
                    st.stop()

                relevant_chunks = get_relevant_chunks(
                    st.session_state.pdf_chunks, user_question
                )
                pdf_context = "\n\n---\n\n".join(relevant_chunks)

            # Call the Study Tutor Agent
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer = ask_tutor(
                            question=user_question,
                            chat_history=chat_history_text,
                            pdf_context=pdf_context,
                        )
                    except ValueError as ve:
                        answer = f"⚠️ Configuration error: {str(ve)}"
                    except Exception as e:
                        answer = (
                            "⚠️ Something went wrong while generating the answer. "
                            "Please try again in a moment.\n\n"
                            f"Technical detail: {str(e)}"
                        )

                st.markdown(answer)

            add_message("assistant", answer)
