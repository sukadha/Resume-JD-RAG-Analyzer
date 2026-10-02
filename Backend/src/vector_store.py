import os
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from chunking import load_and_chunk_documents


# =========================================================
# PATHS
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

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
# CREATE VECTOR STORE DIRECTORY
# =========================================================

os.makedirs(VECTOR_STORE_DIR, exist_ok=True)


# =========================================================
# LOAD EMBEDDING MODEL
# =========================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")


# =========================================================
# BUILD VECTOR STORE
# =========================================================

def build_vector_store():

    print("\n" + "=" * 60)
    print("BUILDING FAISS VECTOR STORE")
    print("=" * 60)

    # -----------------------------------------------------
    # Load chunks
    # -----------------------------------------------------

    chunks = load_and_chunk_documents()

    if not chunks:

        raise ValueError(
            "No chunks found. Run/check chunking.py first."
        )

    print(f"\nTotal chunks: {len(chunks)}")

    # -----------------------------------------------------
    # Extract text
    # -----------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # -----------------------------------------------------
    # Create embeddings
    # -----------------------------------------------------

    print("\nCreating embeddings...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(
        "Embedding shape:",
        embeddings.shape
    )

    # -----------------------------------------------------
    # Create FAISS index
    # -----------------------------------------------------

    dimension = embeddings.shape[1]

    print(
        "\nEmbedding dimension:",
        dimension
    )

    index = faiss.IndexFlatIP(
        dimension
    )

    # -----------------------------------------------------
    # Add vectors
    # -----------------------------------------------------

    index.add(embeddings)

    print(
        "Vectors added to FAISS:",
        index.ntotal
    )

    # -----------------------------------------------------
    # Save FAISS index
    # -----------------------------------------------------

    faiss.write_index(
        index,
        INDEX_PATH
    )

    print(
        "\nFAISS index saved:"
    )

    print(INDEX_PATH)

    # -----------------------------------------------------
    # Save metadata
    # -----------------------------------------------------

    metadata = []

    for chunk in chunks:

        metadata.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "page": chunk["page"],
            "document_type": chunk["document_type"]
        })

    with open(
        METADATA_PATH,
        "wb"
    ) as file:

        pickle.dump(
            metadata,
            file
        )

    print(
        "\nMetadata saved:"
    )

    print(METADATA_PATH)

    # -----------------------------------------------------
    # Verify files
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("VECTOR STORE CREATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"\nFAISS vectors : {index.ntotal}"
    )

    print(
        f"Metadata items: {len(metadata)}"
    )

    print(
        f"\nindex.faiss size: "
        f"{os.path.getsize(INDEX_PATH)} bytes"
    )

    print(
        f"metadata.pkl size: "
        f"{os.path.getsize(METADATA_PATH)} bytes"
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    build_vector_store()