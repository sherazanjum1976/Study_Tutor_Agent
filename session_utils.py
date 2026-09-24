"""
session_utils.py
Handles Streamlit session-state initialization and management
for chat history and PDF context.
"""

import streamlit as st


def init_session_state():
    """
    Initialize all required session-state variables if they don't already exist.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "pdf_chunks" not in st.session_state:
        st.session_state.pdf_chunks = []

    if "pdf_name" not in st.session_state:
        st.session_state.pdf_name = None

    if "study_mode" not in st.session_state:
        st.session_state.study_mode = "General Study"


def add_message(role, content):
    """
    Add a message (user or assistant) to the chat history.
    """
    st.session_state.messages.append({"role": role, "content": content})


def get_chat_history_text(max_messages=6):
    """
    Return the last few messages as plain text, used to give the agent
    conversation context for follow-up questions.
    """
    recent_messages = st.session_state.messages[-max_messages:]
    history_text = ""

    for message in recent_messages:
        role_label = "Student" if message["role"] == "user" else "Tutor"
        history_text += f"{role_label}: {message['content']}\n"

    return history_text


def clear_chat():
    """
    Clear the chat history only (keeps PDF context).
    """
    st.session_state.messages = []


def reset_pdf():
    """
    Remove the uploaded PDF and its chunks from session state.
    """
    st.session_state.pdf_chunks = []
    st.session_state.pdf_name = None


def new_session():
    """
    Reset everything: chat history and PDF context.
    """
    st.session_state.messages = []
    st.session_state.pdf_chunks = []
    st.session_state.pdf_name = None
