import sys
import os
import json
import re

# ============================================================
# IMPORT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from .retriever import retrieve_documents
    from .llm import generate_response
except ImportError:
    from retriever import retrieve_documents
    from llm import generate_response


# ============================================================
# FORMAT RETRIEVED RESULTS
# ============================================================

def format_results(results):

    if not results:
        return "No relevant information found."

    formatted = []

    for i, result in enumerate(results, start=1):

        if isinstance(result, dict):

            text = result.get("text", "")
            source = result.get("source", "Unknown")
            page = result.get("page", "Unknown")

            document_type = result.get(
                "document_type",
                result.get("type", "Unknown")
            )

            score = result.get("score", "")

            formatted.append(
                f"""
--- Retrieved Chunk {i} ---

Source: {source}
Page: {page}
Document Type: {document_type}
Score: {score}

Text:
{text}
"""
            )

        elif isinstance(result, (tuple, list)):

            if len(result) >= 4:

                text = result[0]
                source = result[1]
                page = result[2]
                document_type = result[3]

                formatted.append(
                    f"""
--- Retrieved Chunk {i} ---

Source: {source}
Page: {page}
Document Type: {document_type}

Text:
{text}
"""
                )

            else:

                formatted.append(
                    f"""
--- Retrieved Chunk {i} ---
{result}
"""
                )

        else:

            formatted.append(
                f"""
--- Retrieved Chunk {i} ---
{result}
"""
            )

    return "\n".join(formatted)


# ============================================================
# SEPARATE RESUME AND JD
# ============================================================

def separate_documents(results):

    resume_results = []
    jd_results = []

    for result in results:

        if not isinstance(result, dict):
            continue

        document_type = str(
            result.get(
                "document_type",
                result.get("type", "")
            )
        ).lower().strip()

        source = str(
            result.get("source", "")
        ).lower().strip()

        # ----------------------------
        # RESUME
        # ----------------------------

        if (
            document_type == "resume"
            or "resume" in source
        ):
            resume_results.append(result)

        # ----------------------------
        # JOB DESCRIPTION
        # ----------------------------

        elif (
            document_type in [
                "job_description",
                "job description",
                "jd"
            ]
            or "job_description" in source
            or "job description" in source
            or "job-description" in source
        ):
            jd_results.append(result)

    return resume_results, jd_results


# ============================================================
# BUILD RAG PROMPT
# ============================================================

def build_prompt(
    question,
    resume_context,
    jd_context
):

    prompt = f"""
You are a Resume and Job Description RAG Analyzer.

Your task is to analyze a candidate's resume against a job description.

You MUST use the retrieved resume context and retrieved job-description
context as your primary source of information.

Do NOT invent information.

Do NOT assume a skill exists just because it is common for the role.

Only report skills, projects, certifications, education, internships,
experience, or technologies that are supported by the provided context.

============================================================
USER QUESTION
============================================================

{question}

============================================================
RESUME CONTEXT
============================================================

{resume_context}

============================================================
JOB DESCRIPTION CONTEXT
============================================================

{jd_context}

============================================================
ANALYSIS RULES
============================================================

Compare the Resume against the Job Description.

Determine:

1. Matching skills
2. Partial matching skills
3. Missing skills
4. Relevant projects
5. Resume improvement suggestions
6. Interview questions
7. Technical questions
8. Relevant resume sections

IMPORTANT:

A matching skill means the skill is supported by the resume AND
is required or mentioned in the job description.

A partial match means the resume has a related skill but does not
fully satisfy the job requirement.

A missing skill means the job description requires the skill but
the resume context does not explicitly support it.

Do not put general statements into the matching_skills array.

============================================================
RETURN ONLY VALID JSON
============================================================

Return exactly this structure:

{{
    "matching_skills": [],
    "partial_match_skills": [],
    "missing_skills": [],
    "relevant_projects": [],
    "resume_suggestions": [],
    "interview_questions": [],
    "technical_questions": [],
    "relevant_resume_sections": [],
    "match_percentage": 0
}}

============================================================
JSON RULES
============================================================

- matching_skills must be an array of strings.
- partial_match_skills must be an array of strings.
- missing_skills must be an array of strings.
- relevant_projects must be an array of objects.

Each relevant project object must contain:

{{
    "project": "Project name",
    "reason": "Why this project is relevant"
}}

- resume_suggestions must be an array of strings.
- interview_questions must be an array of strings.
- technical_questions must be an array of strings.
- relevant_resume_sections must be an array of objects.

Each relevant resume section object must contain:

{{
    "section": "Section name",
    "relevance": "Why it is relevant"
}}

- match_percentage must be a number between 0 and 100.

Do not add Markdown.
Do not add ```json.
Do not add explanations outside the JSON.

Return ONLY the JSON object.
"""

    return prompt


# ============================================================
# EXTRACT JSON FROM GEMINI RESPONSE
# ============================================================

def parse_gemini_response(response):

    if response is None:
        raise ValueError("Gemini returned an empty response.")

    # If response is already a dictionary
    if isinstance(response, dict):
        return response

    # Convert to string
    text = str(response).strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # First attempt
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[start:end + 1]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Could not parse Gemini JSON response: {e}"
            )

    raise ValueError(
        "Gemini response does not contain valid JSON."
    )


# ============================================================
# NORMALIZE ANALYSIS
# ============================================================

def normalize_analysis(data):

    if not isinstance(data, dict):
        data = {}

    matching_skills = data.get(
        "matching_skills",
        data.get("matched_skills", [])
    )

    partial_match_skills = data.get(
        "partial_match_skills",
        data.get("partial_matches", [])
    )

    missing_skills = data.get(
        "missing_skills",
        data.get("potential_gaps", [])
    )

    relevant_projects = data.get(
        "relevant_projects",
        []
    )

    resume_suggestions = data.get(
        "resume_suggestions",
        data.get("improvement_suggestions", [])
    )

    interview_questions = data.get(
        "interview_questions",
        []
    )

    technical_questions = data.get(
        "technical_questions",
        []
    )

    relevant_resume_sections = data.get(
        "relevant_resume_sections",
        []
    )

    match_percentage = data.get(
        "match_percentage",
        data.get("match_percent", 0)
    )

    # Ensure arrays
    if not isinstance(matching_skills, list):
        matching_skills = [str(matching_skills)]

    if not isinstance(partial_match_skills, list):
        partial_match_skills = [str(partial_match_skills)]

    if not isinstance(missing_skills, list):
        missing_skills = [str(missing_skills)]

    if not isinstance(relevant_projects, list):
        relevant_projects = []

    if not isinstance(resume_suggestions, list):
        resume_suggestions = [str(resume_suggestions)]

    if not isinstance(interview_questions, list):
        interview_questions = [str(interview_questions)]

    if not isinstance(technical_questions, list):
        technical_questions = [str(technical_questions)]

    if not isinstance(relevant_resume_sections, list):
        relevant_resume_sections = []

    # Convert percentage to number
    try:
        match_percentage = float(match_percentage)
    except Exception:
        match_percentage = 0

    match_percentage = max(
        0,
        min(100, match_percentage)
    )

    # Return one consistent structure
    return {
        "matching_skills": matching_skills,
        "partial_match_skills": partial_match_skills,
        "missing_skills": missing_skills,
        "relevant_projects": relevant_projects,
        "resume_suggestions": resume_suggestions,
        "interview_questions": interview_questions,
        "technical_questions": technical_questions,
        "relevant_resume_sections": relevant_resume_sections,
        "match_percentage": match_percentage
    }


# ============================================================
# MAIN RAG PIPELINE
# ============================================================

def run_rag_pipeline(question):

    print("\n" + "=" * 70)
    print("RAG PIPELINE")
    print("=" * 70)

    print("\nQuestion:")
    print(question)

    # ========================================================
    # STEP 1 — RETRIEVE
    # ========================================================

    print("\nRetrieving resume and job description documents...")

    try:

        try:

            results = retrieve_documents(
                question,
                top_k=12
            )

        except TypeError:

            print(
                "top_k parameter not supported. "
                "Using default retriever."
            )

            results = retrieve_documents(question)

    except Exception as e:

        print("\nRetrieval error:")
        print(e)

        return {
            "status": "error",
            "message": str(e)
        }

    if not results:

        return {
            "status": "error",
            "message": "No documents were retrieved."
        }

    print(
        f"\nTotal chunks retrieved: {len(results)}"
    )

    # ========================================================
    # STEP 2 — SEPARATE DOCUMENTS
    # ========================================================

    resume_results, jd_results = separate_documents(
        results
    )

    print(
        f"Resume chunks retrieved: "
        f"{len(resume_results)}"
    )

    print(
        f"Job Description chunks retrieved: "
        f"{len(jd_results)}"
    )

    # ========================================================
    # FALLBACK
    # ========================================================

    if not resume_results or not jd_results:

        print(
            "\nDocument metadata separation was incomplete."
        )

        # Use retrieved results as combined context
        # rather than returning empty analysis.

        if not resume_results:
            resume_results = results

        if not jd_results:
            jd_results = results

    # ========================================================
    # STEP 3 — FORMAT CONTEXT
    # ========================================================

    resume_context = format_results(
        resume_results
    )

    jd_context = format_results(
        jd_results
    )

    # ========================================================
    # STEP 4 — BUILD PROMPT
    # ========================================================

    print("\nBuilding RAG prompt...")

    prompt = build_prompt(
        question,
        resume_context,
        jd_context
    )

    # ========================================================
    # STEP 5 — GEMINI
    # ========================================================

    print(
        "\nSending retrieved context to Gemini..."
    )

    try:

        response = generate_response(prompt)

    except Exception as e:

        print("\nGemini error:")
        print(e)

        return {
            "status": "error",
            "message": str(e)
        }

    # ========================================================
    # STEP 6 — PARSE JSON
    # ========================================================

    print("\nParsing Gemini response...")

    try:

        parsed = parse_gemini_response(
            response
        )

        analysis = normalize_analysis(
            parsed
        )

    except Exception as e:

        print("\nJSON parsing error:")
        print(e)

        return {
            "status": "error",
            "message": "Invalid JSON returned by Gemini.",
            "raw_response": str(response)
        }

    # ========================================================
    # FINAL RESULT
    # ========================================================

    final_result = {
        "status": "success",
        "analysis": analysis,
        "retrieval": {
            "resume_chunks": len(resume_results),
            "job_description_chunks": len(jd_results)
        }
    }

    print("\n" + "=" * 70)
    print("RAG ANALYSIS RESULT")
    print("=" * 70)

    print(
        json.dumps(
            final_result,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\n" + "=" * 70)

    return final_result


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("RESUME + JD RAG ANALYZER")
    print("=" * 70)

    question = input(
        "\nEnter your question: "
    ).strip()

    if not question:

        print(
            "Question cannot be empty."
        )

    else:

        result = run_rag_pipeline(
            question
        )

        print("\nFINAL RESULT:")

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )