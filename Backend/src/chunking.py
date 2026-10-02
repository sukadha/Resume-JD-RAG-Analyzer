import os
import sys


# =========================================================
# PROJECT PATH
# =========================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.dirname(
    CURRENT_DIR
)

# Make sure src can import file_loader.py
sys.path.append(CURRENT_DIR)


# =========================================================
# IMPORT DOCUMENT LOADER
# =========================================================

from file_loader import load_documents


# =========================================================
# CHUNK SETTINGS
# =========================================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


# =========================================================
# CREATE CHUNKS
# =========================================================

def create_chunks(
    documents,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
):
    """
    Split extracted documents into smaller text chunks.

    Each chunk preserves:
        text
        source
        page
        document_type
    """

    chunks = []

    # -----------------------------------------------------
    # Validate settings
    # -----------------------------------------------------

    if chunk_overlap >= chunk_size:

        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    # -----------------------------------------------------
    # Process every document/page
    # -----------------------------------------------------

    for document in documents:

        text = document["text"].strip()

        if not text:
            continue

        source = document["source"]
        page = document["page"]
        document_type = document["document_type"]

        # -------------------------------------------------
        # Split text
        # -------------------------------------------------

        start = 0
        text_length = len(text)

        while start < text_length:

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({
                    "text": chunk_text,
                    "source": source,
                    "page": page,
                    "document_type": document_type
                })

            # -------------------------------------------------
            # Move forward while keeping overlap
            # -------------------------------------------------

            next_start = end - chunk_overlap

            # Safety check
            if next_start <= start:
                break

            start = next_start

    return chunks


# =========================================================
# LOAD DOCUMENTS AND CREATE CHUNKS
# =========================================================

def load_and_chunk_documents():

    documents = load_documents()

    chunks = create_chunks(
        documents,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    return chunks


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("CHUNKING TEST")
    print("=" * 50)

    # -----------------------------------------------------
    # Load documents
    # -----------------------------------------------------

    documents = load_documents()

    print(
        f"\nDocuments extracted: {len(documents)}"
    )

    if not documents:

        print(
            "\nNo documents found."
        )

        print(
            "\nMake sure these files exist:"
        )

        print(
            "Backend/documents/Resume.pdf"
        )

        print(
            "Backend/documents/Job_Description.pdf"
        )

        sys.exit(0)

    # -----------------------------------------------------
    # Create chunks
    # -----------------------------------------------------

    chunks = create_chunks(
        documents,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    print(
        f"Total chunks: {len(chunks)}"
    )

    # -----------------------------------------------------
    # Display settings
    # -----------------------------------------------------

    print(
        f"\nChunk size: {CHUNK_SIZE}"
    )

    print(
        f"Chunk overlap: {CHUNK_OVERLAP}"
    )

    # -----------------------------------------------------
    # Display first chunk
    # -----------------------------------------------------

    if chunks:

        first_chunk = chunks[0]

        print("\nFirst chunk:")
        print("-" * 50)

        print(
            "Source:",
            first_chunk["source"]
        )

        print(
            "Page:",
            first_chunk["page"]
        )

        print(
            "Document Type:",
            first_chunk["document_type"]
        )

        print("\nText:")
        print(first_chunk["text"])

    # -----------------------------------------------------
    # Display last chunk
    # -----------------------------------------------------

    if len(chunks) > 1:

        last_chunk = chunks[-1]

        print("\nLast chunk:")
        print("-" * 50)

        print(
            "Source:",
            last_chunk["source"]
        )

        print(
            "Page:",
            last_chunk["page"]
        )

        print(
            "Document Type:",
            last_chunk["document_type"]
        )

        print("\nText:")
        print(last_chunk["text"])

    # -----------------------------------------------------
    # Completion
    # -----------------------------------------------------

    print("\n" + "=" * 50)
    print("CHUNKING COMPLETE")
    print("=" * 50)