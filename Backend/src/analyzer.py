import re
from typing import List, Dict, Any

from llm import generate_response


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _clean_text(text: str) -> str:
    """Clean extra whitespace from text."""
    if not text:
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()


def _format_context(results: List[Dict[str, Any]]) -> str:
    """
    Convert retrieved chunks into readable context.
    """

    if not results:
        return "No relevant information was retrieved."

    context = []

    for i, result in enumerate(results, start=1):

        if isinstance(result, dict):

            text = _clean_text(result.get("text", ""))

            source = result.get(
                "source",
                "Unknown"
            )

            page = result.get(
                "page",
                "Unknown"
            )

            document_type = result.get(
                "document_type",
                "Unknown"
            )

            context.append(
                f"""
--- Chunk {i} ---
Source: {source}
Page: {page}
Document Type: {document_type}

Text:
{text}
"""
            )

        else:
            context.append(
                f"""
--- Chunk {i} ---
{result}
"""
            )

    return "\n".join(context)


def _generate(prompt: str) -> str:
    """
    Send a prompt to Gemini.
    """

    try:
        response = generate_response(prompt)

        if response is None:
            return "No response was generated."

        return str(response).strip()

    except Exception as e:
        return f"Analyzer error: {str(e)}"


# ============================================================
# 1. SKILL MATCHING
# ============================================================

def analyze_skill_matching(
    resume_results: List[Dict[str, Any]],
    jd_results: List[Dict[str, Any]]
) -> str:

    resume_context = _format_context(resume_results)
    jd_context = _format_context(jd_results)

    prompt = f"""
You are analyzing a candidate Resume against a Job Description.

TASK:
Identify skills that are explicitly supported by the Resume
and are also explicitly required or mentioned in the Job Description.

RESUME CONTEXT:
{resume_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

RULES:
- Use only the provided context.
- Do not invent skills.
- Do not assume that similar technologies are identical.
- Only report a skill as a match when the Resume supports it.
- Do not create experience that is not present in the Resume.

OUTPUT FORMAT:

## Matching Skills

- Python
- SQL
- Machine Learning

For each skill, briefly mention where it is supported if possible.
"""

    return _generate(prompt)


# ============================================================
# 2. MISSING / POTENTIALLY MISSING SKILLS
# ============================================================

def analyze_missing_skills(
    resume_results: List[Dict[str, Any]],
    jd_results: List[Dict[str, Any]]
) -> str:

    resume_context = _format_context(resume_results)
    jd_context = _format_context(jd_results)

    prompt = f"""
You are comparing a candidate Resume with a Job Description.

TASK:
Identify Job Description skills or requirements that are NOT
explicitly found in the provided Resume context.

RESUME CONTEXT:
{resume_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

IMPORTANT:
- Say "Not found in the resume" or "Potential gap".
- Do NOT say that the candidate definitely lacks a skill.
- Do not invent skills.
- Do not infer that absence from the retrieved chunks means
  the skill is absent from the complete resume.
- Only compare information explicitly present in the provided
  contexts.

OUTPUT FORMAT:

## Potentially Missing Skills

| Skill / Requirement | Evidence from JD | Resume Evidence |
|---|---|---|
| Docker | Required in JD | Not found in retrieved resume context |
| Kubernetes | Required in JD | Not found in retrieved resume context |

Use careful wording.
"""

    return _generate(prompt)


# ============================================================
# 3. RELEVANT PROJECTS
# ============================================================

def analyze_relevant_projects(
    resume_results: List[Dict[str, Any]],
    jd_results: List[Dict[str, Any]]
) -> str:

    resume_context = _format_context(resume_results)
    jd_context = _format_context(jd_results)

    prompt = f"""
You are a Resume and Job Description Analyzer.

TASK:
Identify projects in the Resume that are relevant to the
requirements in the Job Description.

RESUME CONTEXT:
{resume_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

RULES:
- Only mention projects explicitly supported by the Resume.
- Do not invent project technologies.
- Do not invent project results or metrics.
- Explain why the project is relevant based on the JD.

OUTPUT FORMAT:

## Relevant Projects

### Project: <project name>

**JD Requirement:**
<relevant JD requirement>

**Resume Evidence:**
<what the resume says>

**Why Relevant:**
<short explanation>
"""

    return _generate(prompt)


# ============================================================
# 4. RESUME IMPROVEMENT SUGGESTIONS
# ============================================================

def analyze_resume_improvements(
    resume_results: List[Dict[str, Any]],
    jd_results: List[Dict[str, Any]]
) -> str:

    resume_context = _format_context(resume_results)
    jd_context = _format_context(jd_results)

    prompt = f"""
You are reviewing a candidate Resume against a Job Description.

TASK:
Provide resume improvement suggestions based only on the
provided Resume and Job Description.

RESUME CONTEXT:
{resume_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

RULES:
- Do not invent experience.
- Do not invent technologies.
- Do not invent metrics.
- Do not create fake achievements.
- If suggesting metrics, explicitly say they should only be
  added if the candidate has actual evidence for them.
- Focus on improving clarity, relevance, keywords, project
  descriptions and measurable results when supported.

Example:

Current:
"Developed an AI chatbot."

Suggestion:
"Expand the description with the technologies, architecture,
and measurable result if those details are supported by the
candidate's actual experience."

OUTPUT FORMAT:

## Resume Improvement Suggestions

1. Current:
   ...

   Suggestion:
   ...

2. Current:
   ...

   Suggestion:
   ...
"""

    return _generate(prompt)


# ============================================================
# 5. INTERVIEW QUESTIONS BASED ON JD
# ============================================================

def generate_interview_questions(
    jd_results: List[Dict[str, Any]]
) -> str:

    jd_context = _format_context(jd_results)

    prompt = f"""
You are an interview preparation assistant.

TASK:
Generate interview questions based on the Job Description.

JOB DESCRIPTION CONTEXT:
{jd_context}

RULES:
- Questions must be based on technologies, responsibilities,
  and requirements explicitly mentioned in the JD.
- Do not invent requirements.
- Include conceptual and practical questions.
- Do not provide answers unless requested.

OUTPUT FORMAT:

## Interview Questions

### General / Role Questions

1. ...
2. ...
3. ...

### Technical Questions

1. ...
2. ...
3. ...

### Practical / Scenario Questions

1. ...
2. ...
3. ...
"""

    return _generate(prompt)


# ============================================================
# 6. TECHNICAL QUESTIONS BASED ON RESUME
# ============================================================

def generate_resume_technical_questions(
    resume_results: List[Dict[str, Any]]
) -> str:

    resume_context = _format_context(resume_results)

    prompt = f"""
You are preparing technical interview questions based on
a candidate's Resume.

RESUME CONTEXT:
{resume_context}

TASK:
Generate technical questions based only on technologies,
projects, tools, frameworks and concepts explicitly supported
by the Resume.

RULES:
- Do not invent skills.
- Do not ask about technologies that are not present in the
  provided Resume context.
- Include questions about projects where appropriate.
- Include basic, intermediate and advanced questions.

OUTPUT FORMAT:

## Technical Questions Based on Resume

### Python

1. ...
2. ...

### Machine Learning

1. ...
2. ...

### NLP / Generative AI

1. ...
2. ...

### Projects

1. ...
2. ...
"""

    return _generate(prompt)


# ============================================================
# 7. SECTION RELEVANCE
# ============================================================

def analyze_section_relevance(
    resume_results: List[Dict[str, Any]],
    jd_results: List[Dict[str, Any]]
) -> str:

    resume_context = _format_context(resume_results)
    jd_context = _format_context(jd_results)

    prompt = f"""
You are analyzing which Resume sections are relevant to a
Job Description.

RESUME CONTEXT:
{resume_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

TASK:
Identify Resume sections, projects, internships, skills,
certifications or education that are relevant to the JD.

RULES:
- Use only information supported by the Resume.
- Do not invent sections.
- Explain why each section is relevant to the JD.
- Clearly distinguish Resume evidence from JD requirements.

OUTPUT FORMAT:

## Relevant Resume Sections

### Section: Projects

**Relevant because:**
...

**Resume Evidence:**
...

**JD Requirement:**
...

### Section: Skills

**Relevant because:**
...

### Section: Internships / Experience

**Relevant because:**
...
"""

    return _generate(prompt)


# ============================================================
# RUN COMPLETE ANALYSIS
# ============================================================

def analyze_resume_against_jd(
    resume_results: List[Dict[str, Any]],
    jd_results: List[Dict[str, Any]]
) -> Dict[str, str]:

    print("\n" + "=" * 70)
    print("RUNNING RESUME-JD ANALYSIS")
    print("=" * 70)

    print("\n1. Analyzing matching skills...")

    matching_skills = analyze_skill_matching(
        resume_results,
        jd_results
    )

    print("\n2. Analyzing potentially missing skills...")

    missing_skills = analyze_missing_skills(
        resume_results,
        jd_results
    )

    print("\n3. Finding relevant projects...")

    relevant_projects = analyze_relevant_projects(
        resume_results,
        jd_results
    )

    print("\n4. Generating resume improvement suggestions...")

    resume_improvements = analyze_resume_improvements(
        resume_results,
        jd_results
    )

    print("\n5. Generating JD interview questions...")

    interview_questions = generate_interview_questions(
        jd_results
    )

    print("\n6. Generating resume-based technical questions...")

    technical_questions = generate_resume_technical_questions(
        resume_results
    )

    print("\n7. Analyzing relevant resume sections...")

    section_relevance = analyze_section_relevance(
        resume_results,
        jd_results
    )

    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "relevant_projects": relevant_projects,
        "resume_improvements": resume_improvements,
        "interview_questions": interview_questions,
        "technical_questions": technical_questions,
        "section_relevance": section_relevance,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("ANALYZER TEST")
    print("=" * 70)

    print("""
This file contains analysis functions.

The functions are normally called from rag_pipeline.py
after Resume and Job Description chunks have been retrieved.

Example:

from analyzer import analyze_resume_against_jd

result = analyze_resume_against_jd(
    resume_results,
    jd_results
)
""")

    print("=" * 70)
    print("ANALYZER MODULE READY")
    print("=" * 70)