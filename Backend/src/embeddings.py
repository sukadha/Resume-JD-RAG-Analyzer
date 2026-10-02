import os
import sys
import numpy as np


# =========================================================
# PROJECT PATHS
# =========================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.dirname(
    CURRENT_DIR
)

if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)


# =========================================================
# IMPORT SENTENCE TRANSFORMER
# =========================================================

from sentence_transformers import SentenceTransformer


# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODEL_NAME = "all-MiniLM-L6-v2"

EMBEDDING_DIMENSION = 384


# =========================================================
# LOAD MODEL
# =========================================================

print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Embedding model loaded successfully.")


# =========================================================
# GENERATE EMBEDDINGS FOR CHUNKS
# =========================================================

def generate_embeddings(chunks):
    """
    Generate embeddings for document chunks.

    Input:
        [
            {
                "text": "...",
                "source": "Resume.pdf",
                "page": 1,
                "document_type": "resume"
            }
        ]

    Output:
        NumPy array with shape:
        (number_of_chunks, 384)
    """

    if not chunks:
        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    return embeddings


# =========================================================
# GENERATE SINGLE EMBEDDING
# =========================================================

def generate_single_embedding(text):
    """
    Generate an embedding for a single text.

    This function will later be used for:
        User Question
             ↓
        Embedding
             ↓
        FAISS Search
    """

    if not text or not text.strip():

        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32
        )

    embedding = model.encode(
        text.strip(),
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    return embedding


# =========================================================
# EMBEDDING DIMENSION
# =========================================================

def get_embedding_dimension():

    return EMBEDDING_DIMENSION


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 50)
    print("EMBEDDING TEST")
    print("=" * 50)

    # -----------------------------------------------------
    # Import chunking functions
    # -----------------------------------------------------

    from chunking import load_and_chunk_documents

    # -----------------------------------------------------
    # Load chunks
    # -----------------------------------------------------

    print("\nLoading chunks...")

    chunks = load_and_chunk_documents()

    print(
        f"Number of chunks: {len(chunks)}"
    )

    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    print("\nGenerating embeddings...")

    embeddings = generate_embeddings(
        chunks
    )

    # -----------------------------------------------------
    # Display shape
    # -----------------------------------------------------

    print("\nEmbedding shape:")

    print(
        embeddings.shape
    )

    # -----------------------------------------------------
    # Display dimension
    # -----------------------------------------------------

    print("\nEmbedding dimension:")

    print(
        embeddings.shape[1]
        if len(embeddings) > 0
        else EMBEDDING_DIMENSION
    )

    # -----------------------------------------------------
    # Display first vector
    # -----------------------------------------------------

    if len(embeddings) > 0:

        print("\nFirst vector:")

        print(
            embeddings[0]
        )

        print(
            "\nFirst vector length:",
            len(embeddings[0])
        )

    # -----------------------------------------------------
    # Test single question embedding
    # -----------------------------------------------------

    question = (
        "What skills are required for this job?"
    )

    print("\nTesting single question embedding:")

    print(
        f"Question: {question}"
    )

    question_embedding = (
        generate_single_embedding(
            question
        )
    )

    print(
        "Question embedding shape:",
        question_embedding.shape
    )

    # -----------------------------------------------------
    # Finish
    # -----------------------------------------------------

    print("\n" + "=" * 50)
    print("EMBEDDING TEST COMPLETE")
    print("=" * 50)