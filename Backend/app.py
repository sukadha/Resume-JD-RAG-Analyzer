import os
import json
import traceback

from flask import Flask, request, jsonify
from flask_cors import CORS

from src.rag_pipeline import run_rag_pipeline


# ============================================================
# APP CONFIG
# ============================================================

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DOCUMENTS_DIR = os.path.join(
    BASE_DIR,
    "documents"
)

os.makedirs(
    DOCUMENTS_DIR,
    exist_ok=True
)


# ============================================================
# HEALTH
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "success",
        "message": "Resume JD RAG Analyzer API is running."
    })


# ============================================================
# GET ANALYZE
# ============================================================

@app.route(
    "/api/analyze",
    methods=["GET"]
)
def analyze_get():

    return jsonify({
        "status": "error",
        "message": "Method not allowed for this endpoint.",
        "hint": "Use POST /api/analyze for Resume + Job Description analysis."
    }), 405


# ============================================================
# POST ANALYZE
# ============================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    print("\n" + "=" * 70)
    print("RESUME JD ANALYSIS REQUEST")
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # CHECK FILES
        # ----------------------------------------------------

        resume_file = request.files.get(
            "resume"
        )

        jd_file = request.files.get(
            "job_description"
        )

        question = request.form.get(
            "question",
            "Analyze my resume with this job description and show the skill match."
        )

        if resume_file is None:

            return jsonify({
                "status": "error",
                "message": "Resume PDF is required."
            }), 400

        if jd_file is None:

            return jsonify({
                "status": "error",
                "message": "Job Description PDF is required."
            }), 400

        # ----------------------------------------------------
        # VALIDATE PDF
        # ----------------------------------------------------

        resume_name = resume_file.filename

        jd_name = jd_file.filename

        if not resume_name.lower().endswith(".pdf"):

            return jsonify({
                "status": "error",
                "message": "Resume must be a PDF file."
            }), 400

        if not jd_name.lower().endswith(".pdf"):

            return jsonify({
                "status": "error",
                "message": "Job Description must be a PDF file."
            }), 400

        # ----------------------------------------------------
        # SAVE FILES
        # ----------------------------------------------------

        resume_path = os.path.join(
            DOCUMENTS_DIR,
            "Resume.pdf"
        )

        jd_path = os.path.join(
            DOCUMENTS_DIR,
            "Job_Description.pdf"
        )

        resume_file.save(
            resume_path
        )

        jd_file.save(
            jd_path
        )

        print(
            f"\nResume saved: {resume_path}"
        )

        print(
            f"JD saved: {jd_path}"
        )

        print(
            f"Question: {question}"
        )

        # ----------------------------------------------------
        # RUN RAG
        # ----------------------------------------------------

        print(
            "\nRunning RAG pipeline..."
        )

        result = run_rag_pipeline(
            question
        )

        # ----------------------------------------------------
        # CHECK RESULT
        # ----------------------------------------------------

        if result is None:

            return jsonify({
                "status": "error",
                "message": "RAG pipeline returned no analysis.",
                "data": None
            }), 500

        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        response = {
            "status": "success",
            "message": "Resume and Job Description analyzed successfully.",
            "data": result
        }

        print(
            "\nReturning analysis to frontend..."
        )

        print(
            json.dumps(
                response,
                indent=4,
                ensure_ascii=False
            )
        )

        return jsonify(
            response
        ), 200

    except Exception as e:

        print("\nRAG API ERROR")
        print(str(e))

        traceback.print_exc()

        return jsonify({
            "status": "error",
            "message": str(e),
            "data": None
        }), 500


# ============================================================
# ROOT
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({
        "name": "Resume-JD RAG Analyzer API",
        "status": "running",
        "endpoints": {
            "health": "GET /api/health",
            "analyze": "POST /api/analyze"
        }
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "\nRESUME-JD RAG ANALYZER API"
    )

    print(
        "\nAvailable endpoints:"
    )

    print(
        "GET  /api/health"
    )

    print(
        "GET  /api/analyze"
    )

    print(
        "POST /api/analyze"
    )

    print(
        "\nServer starting ..."
    )

    print(
        "http://127.0.0.1:5000"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )