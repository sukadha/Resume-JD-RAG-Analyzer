import os
import fitz


# =========================================================
# PROJECT PATHS
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

DOCUMENTS_DIR = os.path.join(
    BACKEND_DIR,
    "documents"
)


# =========================================================
# LOAD PDF
# =========================================================

def load_pdf(file_path, document_type):
    """
    Extract text from a PDF page by page.

    Returns:
        [
            {
                "text": "...",
                "source": "Resume.pdf",
                "page": 1,
                "document_type": "resume"
            }
        ]
    """

    documents = []

    filename = os.path.basename(file_path)

    try:
        pdf = fitz.open(file_path)

        for page_number, page in enumerate(pdf, start=1):

            text = page.get_text("text").strip()

            # Skip completely empty pages
            if not text:
                continue

            documents.append({
                "text": text,
                "source": filename,
                "page": page_number,
                "document_type": document_type
            })

        pdf.close()

        return documents

    except Exception as e:

        print(f"Error loading {filename}: {e}")

        return []


# =========================================================
# LOAD RESUME
# =========================================================

def load_resume():
    """
    Load Resume.pdf from documents folder.
    """

    resume_path = os.path.join(
        DOCUMENTS_DIR,
        "Resume.pdf"
    )

    if not os.path.exists(resume_path):

        print("Resume.pdf not found.")

        return []

    return load_pdf(
        resume_path,
        "resume"
    )


# =========================================================
# LOAD JOB DESCRIPTION
# =========================================================

def load_job_description():
    """
    Load Job_Description.pdf from documents folder.
    """

    jd_path = os.path.join(
        DOCUMENTS_DIR,
        "Job_Description.pdf"
    )

    if not os.path.exists(jd_path):

        print("Job_Description.pdf not found.")

        return []

    return load_pdf(
        jd_path,
        "job_description"
    )


# =========================================================
# LOAD ALL DOCUMENTS
# =========================================================

def load_documents():

    resume_documents = load_resume()

    jd_documents = load_job_description()

    all_documents = (
        resume_documents +
        jd_documents
    )

    return all_documents


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 40)
    print("DOCUMENT LOADER TEST")
    print("=" * 40)

    # -----------------------------------------------------
    # Load Resume
    # -----------------------------------------------------

    resume_documents = load_resume()

    if resume_documents:

        resume_pages = len(resume_documents)

        print("\nResume loaded successfully.")
        print(f"Resume pages: {resume_pages}")

    else:

        print("\nResume could not be loaded.")


    # -----------------------------------------------------
    # Load Job Description
    # -----------------------------------------------------

    jd_documents = load_job_description()

    if jd_documents:

        jd_pages = len(jd_documents)

        print("\nJob Description loaded successfully.")
        print(f"JD pages: {jd_pages}")

    else:

        print("\nJob Description could not be loaded.")


    # -----------------------------------------------------
    # Total
    # -----------------------------------------------------

    all_documents = (
        resume_documents +
        jd_documents
    )

    print("\nTotal pages extracted:", len(all_documents))


    # -----------------------------------------------------
    # Display first document
    # -----------------------------------------------------

    if all_documents:

        print("\nFirst extracted document:")
        print("-" * 40)

        first = all_documents[0]

        print("Source:", first["source"])
        print("Page:", first["page"])
        print("Document Type:", first["document_type"])

        print("\nText:")
        print(first["text"][:500])

    print("\n" + "=" * 40)
    print("TEST COMPLETE")
    print("=" * 40)