"""Pytest configuration and test environment initialization."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Pre-initialize faiss before pytest runner hooks
try:
    import faiss  # noqa: F401
except Exception:
    pass
