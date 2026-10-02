import os

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# GEMINI API KEY
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# MODEL
# =========================================================

MODEL_NAME = "gemini-3.8-flash"


# =========================================================
# GENERATE RAG ANSWER
# =========================================================

def generate_answer(
    question,
    retrieved_documents
):
    """
    Generate an answer using Gemini and
    retrieved Resume/JD context.
    """

    if not retrieved_documents:
        return "No relevant information was retrieved."

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context_parts = []

    for i, document in enumerate(
        retrieved_documents,
        start=1
    ):

        source = document.get(
            "source",
            "Unknown"
        )

        page = document.get(
            "page",
            "Unknown"
        )

        document_type = document.get(
            "document_type",
            "Unknown"
        )

        text = document.get(
            "text",
            ""
        )

        context_parts.append(
            f"""
--- CONTEXT {i} ---
Source: {source}
Page: {page}
Document Type: {document_type}

{text}
"""
        )

    context = "\n".join(
        context_parts
    )

    # -----------------------------------------------------
    # RAG prompt
    # -----------------------------------------------------

    prompt = f"""
You are an AI Resume and Job Description Analyzer.

Your task is to answer the user's question using ONLY
the retrieved context provided below.

Do not invent information that is not present in the
retrieved context.

If the information is not available in the context,
clearly say that the information was not found.

When useful, mention the source document and page.

==================================================
RETRIEVED CONTEXT
==================================================

{context}

==================================================
USER QUESTION
==================================================

{question}

==================================================
INSTRUCTIONS
==================================================

1. Analyze the Resume and Job Description context.
2. Answer the user's question clearly.
3. Compare Resume information with JD information
   when the question requires comparison.
4. Do not make up skills, experience, projects,
   qualifications, or requirements.
5. Mention relevant source pages when possible.
6. Use bullet points when appropriate.
7. Keep the answer professional and concise.
"""

    # -----------------------------------------------------
    # Gemini request
    # -----------------------------------------------------

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


# =========================================================
# SIMPLE GEMINI TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GEMINI LLM TEST")
    print("=" * 60)

    test_documents = [

        {
            "text": """
            Candidate has experience with Python,
            Flask, Machine Learning, SQL and React.
            """,

            "source": "Resume.pdf",

            "page": 1,

            "document_type": "resume"
        },

        {
            "text": """
            Required skills include Python, SQL,
            Docker, AWS, LangGraph, RAG and FastAPI.
            """,

            "source": "Job_Description.pdf",

            "page": 1,

            "document_type": "job_description"
        }

    ]

    question = "What skills are missing from the candidate's resume?"

    print("\nQuestion:")
    print(question)

    print("\nGenerating answer...\n")

    answer = generate_answer(
        question,
        test_documents
    )

    print("=" * 60)
    print("GEMINI RESPONSE")
    print("=" * 60)

    print(answer)

    print("\n" + "=" * 60)
    print("LLM TEST COMPLETE")
    print("=" * 60)