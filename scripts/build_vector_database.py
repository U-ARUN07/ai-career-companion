"""Script to build and persist the FAISS vector database from internship dataset.

Reads data/internships.json, converts records to comprehensive text representations,
generates normalized embeddings via SentenceTransformers, builds a FAISS FlatIP index,
and serializes both the binary vector index and metadata mapping to disk.
"""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config import settings
from app.services.embedding_service import embedding_service
from app.services.internship_loader import InternshipLoader
from app.services.vector_store import vector_store


def build_and_save_vector_database():
    """Main workflow to build and persist the FAISS vector store."""
    print("=" * 70)
    print("Infosys Springboard VIP 7.0 - RAG Internship Matching System")
    print("Vector Database Builder")
    print("=" * 70)

    start_time = time.time()

    # 1. Load internships
    loader = InternshipLoader(settings.internships_file)
    print(f"\n[1/4] Loading internship dataset from: {settings.internships_file}")
    internships = loader.load_dataset()
    print(f"      -> Successfully loaded and validated {len(internships)} internships.")

    # 2. Format embedding texts
    print("\n[2/4] Formatting text representations for each internship...")
    internship_texts = [
        InternshipLoader.format_internship_to_text(item) for item in internships
    ]
    sample_preview = internship_texts[0][:120] + "..." if internship_texts else ""
    print(f"      -> Sample text preview:\n         \"{sample_preview}\"")

    # 3. Generate embeddings
    print(f"\n[3/4] Generating embeddings using '{settings.embedding_model}'...")
    embeddings = embedding_service.encode_batch(internship_texts)
    print(f"      -> Generated {embeddings.shape[0]} embeddings of dimension {embeddings.shape[1]}.")

    # 4. Build FAISS index & save to disk
    print("\n[4/4] Building FAISS IndexFlatIP (Cosine Similarity) & persisting to disk...")
    vector_store.build_vector_index(internships, embeddings)
    idx_path, meta_path = vector_store.save_vector_index(
        settings.faiss_index_file, settings.metadata_file
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("VECTOR DATABASE BUILD COMPLETE")
    print(f"Total Internships Indexed: {vector_store.get_total_indexed()}")
    print(f"Embedding Dimension:       {embeddings.shape[1]}")
    print(f"FAISS Index File:          {idx_path}")
    print(f"Metadata File:             {meta_path}")
    print(f"Build Time:                {elapsed:.2f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    build_and_save_vector_database()
