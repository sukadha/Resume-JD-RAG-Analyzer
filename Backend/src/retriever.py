import os
import sys
import pickle

import faiss
import numpy as np


# =========================================================
# PROJECT PATHS
# =========================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    CURRENT_DIR
)

VECTOR_STORE_DIR = os.path.join(
    PROJECT_DIR,
    "vector_store"
)

INDEX_PATH = os.path.join(
    VECTOR_STORE_DIR,
    "index.faiss"
)

METADATA_PATH = os.path.join(
    VECTOR_STORE_DIR,
    "metadata.pkl"
)


# =========================================================
# IMPORT EMBEDDING FUNCTION
# =========================================================

if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from embeddings import generate_single_embedding


# =========================================================
# LOAD FAISS INDEX
# =========================================================

def load_index():

    if not os.path.exists(INDEX_PATH):

        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    index = faiss.read_index(
        INDEX_PATH
    )

    return index


# =========================================================
# LOAD METADATA
# =========================================================

def load_metadata():

    if not os.path.exists(METADATA_PATH):

        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_PATH}"
        )

    with open(
        METADATA_PATH,
        "rb"
    ) as file:

        metadata = pickle.load(file)

    return metadata


# =========================================================
# FILTER METADATA
# =========================================================

def get_allowed_document_types(source):

    """
    source can be:

        resume
        job_description
        both
    """

    if source == "resume":

        return ["resume"]

    elif source == "job_description":

        return ["job_description"]

    elif source == "both":

        return [
            "resume",
            "job_description"
        ]

    else:

        raise ValueError(
            "source must be 'resume', "
            "'job_description', or 'both'"
        )


# =========================================================
# RETRIEVE DOCUMENTS
# =========================================================

def retrieve_documents(
    question,
    top_k=5,
    source="both"
):

    """
    Retrieve relevant chunks for a question.

    Parameters
    ----------
    question : str
        User question.

    top_k : int
        Number of final chunks to return.

    source : str
        resume
        job_description
        both

    Returns
    -------
    list
        Relevant document chunks.
    """

    if not question or not question.strip():

        return []

    # -----------------------------------------------------
    # Validate source
    # -----------------------------------------------------

    allowed_types = get_allowed_document_types(
        source
    )

    # -----------------------------------------------------
    # Load FAISS index
    # -----------------------------------------------------

    index = load_index()

    # -----------------------------------------------------
    # Load metadata
    # -----------------------------------------------------

    metadata = load_metadata()

    if not metadata:

        return []

    # -----------------------------------------------------
    # Create question embedding
    # -----------------------------------------------------

    question_embedding = generate_single_embedding(
        question
    )

    # FAISS requires shape:
    #
    # (1, dimension)
    # -----------------------------------------------------

    question_embedding = np.asarray(
        question_embedding,
        dtype=np.float32
    ).reshape(
        1,
        -1
    )

    # -----------------------------------------------------
    # Search more candidates than needed
    # -----------------------------------------------------
    #
    # We retrieve many candidates first because we may
    # need to filter by document type.
    #
    # Example:
    #
    # top_k = 3
    #
    # We search 30 candidates and then keep the
    # relevant Resume/JD chunks.
    # -----------------------------------------------------

    search_k = min(
        max(top_k * 10, 20),
        index.ntotal
    )

    distances, indices = index.search(
        question_embedding,
        search_k
    )

    # -----------------------------------------------------
    # Collect results
    # -----------------------------------------------------

    results = []

    for distance, index_id in zip(
        distances[0],
        indices[0]
    ):

        # FAISS can return -1 when there are not
        # enough results.
        if index_id < 0:
            continue

        # Safety check
        if index_id >= len(metadata):
            continue

        item = metadata[index_id]

        document_type = item.get(
            "document_type",
            ""
        )

        # -------------------------------------------------
        # Filter Resume / JD
        # -------------------------------------------------

        if document_type not in allowed_types:
            continue

        # -------------------------------------------------
        # Create result
        # -------------------------------------------------

        result = {
            "text": item.get(
                "text",
                ""
            ),
            "source": item.get(
                "source",
                ""
            ),
            "page": item.get(
                "page",
                None
            ),
            "document_type": document_type,
            "score": float(distance)
        }

        results.append(
            result
        )

        # Stop after enough filtered results
        if len(results) >= top_k:
            break

    return results


# =========================================================
# PRINT RESULTS
# =========================================================

def print_results(
    question,
    results,
    source
):

    print("\n" + "=" * 60)
    print("RETRIEVER RESULTS")
    print("=" * 60)

    print(
        f"\nQuestion: {question}"
    )

    print(
        f"Search source: {source}"
    )

    print(
        f"Results found: {len(results)}"
    )

    if not results:

        print("\nNo relevant results found.")

        return

    print("\nTop results:")

    for i, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{i}."
        )

        print(
            "Source:",
            result["source"]
        )

        print(
            "Page:",
            result["page"]
        )

        print(
            "Document Type:",
            result["document_type"]
        )

        print(
            "Score:",
            round(
                result["score"],
                4
            )
        )

        print(
            "Text:"
        )

        print(
            result["text"][:300]
        )

        print(
            "-" * 50
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("RETRIEVER TEST")
    print("=" * 60)

    # -----------------------------------------------------
    # TEST 1 — RESUME
    # -----------------------------------------------------

    question_1 = (
        "What Python skills does the candidate have?"
    )

    results_1 = retrieve_documents(
        question=question_1,
        top_k=3,
        source="resume"
    )

    print_results(
        question_1,
        results_1,
        "resume"
    )

    # -----------------------------------------------------
    # TEST 2 — JOB DESCRIPTION
    # -----------------------------------------------------

    question_2 = (
        "What skills are required for this job?"
    )

    results_2 = retrieve_documents(
        question=question_2,
        top_k=3,
        source="job_description"
    )

    print_results(
        question_2,
        results_2,
        "job_description"
    )

    # -----------------------------------------------------
    # TEST 3 — BOTH
    # -----------------------------------------------------

    question_3 = (
        "What skills are mentioned in the resume "
        "and job description?"
    )

    results_3 = retrieve_documents(
        question=question_3,
        top_k=5,
        source="both"
    )

    print_results(
        question_3,
        results_3,
        "both"
    )

    print("\n" + "=" * 60)
    print("RETRIEVER TEST COMPLETE")
    print("=" * 60)