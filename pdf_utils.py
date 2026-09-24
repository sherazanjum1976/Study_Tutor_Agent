"""
pdf_utils.py
Handles PDF text extraction, cleaning, chunking, and simple keyword-based
retrieval of relevant chunks for the Study Tutor Agent.
"""

import re
import fitz  # PyMuPDF


def extract_text_from_pdf(uploaded_file):
    """
    Extract raw text from an uploaded PDF file (a Streamlit UploadedFile object).
    Returns the extracted text as a string, or an empty string if extraction fails.
    """
    try:
        pdf_bytes = uploaded_file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        full_text = ""
        for page in pdf_document:
            full_text += page.get_text()

        pdf_document.close()
        return full_text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def clean_text(text):
    """
    Clean extracted PDF text by collapsing extra whitespace and blank lines.
    """
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def chunk_text(text, chunk_size=800, overlap=100):
    """
    Split cleaned text into overlapping chunks.
    chunk_size and overlap are measured in characters.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap
        if start < 0:
            start = 0

    return chunks


def get_relevant_chunks(chunks, question, top_n=3):
    """
    Simple keyword-based retrieval (no external vector database needed).
    Scores each chunk by how many times the question's keywords appear
    in it, then returns the top_n highest scoring chunks.
    """
    if not chunks:
        return []

    # Extract simple keywords from the question (words longer than 2 letters)
    question_words = re.findall(r"\w+", question.lower())
    keywords = [word for word in question_words if len(word) > 2]

    if not keywords:
        return chunks[:top_n]

    scored_chunks = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(chunk_lower.count(keyword) for keyword in keywords)
        scored_chunks.append((score, chunk))

    # Sort chunks by score, highest first
    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    top_chunks = [chunk for score, chunk in scored_chunks[:top_n] if score > 0]

    # If no chunk matched any keyword, fall back to the first few chunks
    if not top_chunks:
        return chunks[:top_n]

    return top_chunks


def process_pdf(uploaded_file):
    """
    Full pipeline: extract, clean, and chunk a PDF file.
    Returns a list of text chunks, or an empty list if the PDF has no usable text.
    """
    raw_text = extract_text_from_pdf(uploaded_file)
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned)
    return chunks
