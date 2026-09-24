# 📘 Study Tutor Agent

An AI-powered personal study assistant built with Streamlit, CrewAI, and Groq.
Students can ask general academic questions or upload a single PDF and ask
questions specifically about that document.

## Features

- 💬 Chat-based study assistant with session memory (follow-up questions work)
- 📄 Optional PDF mode: upload one PDF and ask questions about it
- 🔍 Simple, lightweight local text retrieval (no external vector database)
- 🧠 Single CrewAI agent powered by Groq's `openai/gpt-oss-120b` model
- 🎨 Modern dark UI with neon blue/cyan accents
- 🔄 Clear Chat / New Session and Remove PDF buttons
- ⚠️ Friendly error handling (missing API key, bad PDFs, API errors, etc.)

## Technology Stack

| Layer          | Technology            |
|----------------|------------------------|
| UI             | Streamlit              |
| Agent framework| CrewAI (single agent)  |
| LLM            | Groq (`openai/gpt-oss-120b`) |
| PDF extraction | PyMuPDF (`fitz`)       |
| Memory         | `st.session_state`     |

## Project Structure

```text
study-tutor-agent/
│
├── app.py              # Main Streamlit app (UI, chat, sidebar)
├── tutor_agent.py       # Groq + CrewAI agent configuration
├── pdf_utils.py         # PDF extraction, cleaning, chunking, retrieval
├── session_utils.py     # Session-state management
├── requirements.txt      # Dependencies
├── README.md
└── .gitignore
```

## How PDF Mode Works

1. Select **Ask from PDF** in the sidebar and upload one PDF.
2. The app extracts the text with PyMuPDF, cleans it, and splits it into
   overlapping chunks.
3. When you ask a question, the app scores each chunk by keyword overlap
   with your question and picks the most relevant chunks.
4. Those chunks are sent to the Study Tutor Agent as context. The agent
   answers primarily from the PDF, and clearly says so if the answer isn't
   in the document — it never invents PDF content.

Switch back to **General Study** at any time to ask normal academic
questions without the PDF.

## Session Memory

All chat history and PDF data live in `st.session_state` — no database is
used. This means:

- Follow-up questions use the recent conversation as context.
- Refreshing/closing the browser tab clears the session.
- **Clear Chat / New Session** resets the chat and the PDF.
- **Remove PDF** clears only the uploaded PDF, keeping the chat.

## API Key Setup

The app needs a Groq API key, read from the `GROQ_API_KEY` environment
variable. **Never hardcode your API key in the code.**

Get a free key at: https://console.groq.com

### Local development

Create a file `.streamlit/secrets.toml` (already excluded by `.gitignore`):

```toml
GROQ_API_KEY = "your_real_groq_api_key_here"
```

Then run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub Upload (no command line needed)

1. Go to [github.com](https://github.com) and create a new repository named
   `study-tutor-agent`.
2. Click **Add file → Create new file** for each file in the project
   structure above (`app.py`, `tutor_agent.py`, `pdf_utils.py`,
   `session_utils.py`, `requirements.txt`, `README.md`, `.gitignore`).
3. Paste the matching code into each file and commit it.
4. Double-check the repository structure matches the layout above.
5. **Do not** upload `.env`, your real API key, or any PDF files.

## Streamlit Cloud Deployment

1. Go to [share.streamlit.io](https://share.streamlit.io) (Streamlit
   Community Cloud).
2. Sign in with your GitHub account.
3. Click **Create app**, then choose **From an existing repo**.
4. Select the `study-tutor-agent` repository.
5. Select the **main** branch.
6. Set the main file path to:

   ```text
   app.py
   ```

7. Before deploying, open **Advanced settings → Secrets** and add:

   ```toml
   GROQ_API_KEY = "YOUR_GROQ_API_KEY"
   ```

8. Click **Deploy**.
9. If something goes wrong, click **Manage app** (bottom right) to open the
   live **logs** panel and see the error details.

## Final Checklist

- [ ] Files uploaded
- [ ] Repository structure verified
- [ ] Secret (`GROQ_API_KEY`) configured
- [ ] `app.py` selected as main file
- [ ] Application deployed
- [ ] General Study mode tested
- [ ] PDF Study mode tested
- [ ] Follow-up questions tested
- [ ] Clear Chat tested
- [ ] PDF Reset tested
