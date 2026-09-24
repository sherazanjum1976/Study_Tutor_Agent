"""
tutor_agent.py
Configures the Groq LLM and the single CrewAI Study Tutor Agent.
"""

import os
from crewai import Agent, Task, Crew, LLM


def get_llm():
    """
    Create and return the LLM configuration used by the Study Tutor Agent.
    CrewAI uses LiteLLM under the hood, which supports Groq models directly
    through the "groq/<model-name>" format. The GROQ_API_KEY environment
    variable is read automatically.
    """
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Please set it as an environment variable "
            "or in Streamlit Secrets."
        )

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=api_key,
        temperature=0.4,
    )
    return llm


def build_tutor_agent():
    """
    Build the single Study Tutor CrewAI Agent.
    """
    llm = get_llm()

    tutor = Agent(
        role="Study Tutor",
        goal=(
            "Help students understand academic topics clearly by explaining "
            "concepts step by step, giving examples, and answering follow-up "
            "questions accurately."
        ),
        backstory=(
            "You are a friendly, patient, and knowledgeable study tutor. "
            "You specialize in breaking down complex topics into simple, "
            "easy-to-understand explanations for students of all levels. "
            "You always answer honestly and you never make up information."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    return tutor


def build_task(tutor, question, chat_history, pdf_context=None):
    """
    Build the CrewAI Task for the current question.
    If pdf_context is provided, the tutor must answer primarily from it.
    """
    if pdf_context:
        task_description = f"""
You are answering a question using the context provided below from an
uploaded PDF document. Follow these rules strictly:

1. Answer primarily using the PDF context below.
2. If the answer is not found in the PDF context, clearly tell the student:
   "I could not find this information in the uploaded document."
3. Do not invent information and claim it came from the PDF.
4. Use clear Markdown formatting (headings, bullet points, bold text).
5. Use the conversation history only to understand follow-up questions,
   not as a source of facts.

Conversation history (for context only):
{chat_history}

PDF Context:
{pdf_context}

Student's Question:
{question}

Provide a clear, structured, educational answer.
"""
    else:
        task_description = f"""
You are a Study Tutor helping a student with a general academic question.
Follow these rules strictly:

1. Explain the concept clearly and step by step.
2. Give a simple example when it is useful.
3. Use the conversation history to understand follow-up questions.
4. Use clear Markdown formatting (headings, bullet points, bold text).
5. Do not hallucinate facts; if you are unsure, say so honestly.

Conversation history (for context only):
{chat_history}

Student's Question:
{question}

Provide a clear, structured, educational answer.
"""

    task = Task(
        description=task_description,
        expected_output="A clear, well-formatted, educational answer in Markdown.",
        agent=tutor,
    )
    return task


def ask_tutor(question, chat_history, pdf_context=None):
    """
    Run the Study Tutor Agent on a single question and return its answer as text.
    """
    tutor = build_tutor_agent()
    task = build_task(tutor, question, chat_history, pdf_context)

    crew = Crew(
        agents=[tutor],
        tasks=[task],
        verbose=False,
    )

    result = crew.kickoff()

    # crew.kickoff() returns a CrewOutput object; convert it to plain text
    answer_text = str(result)
    return answer_text
