"""Pytest configuration and fixtures."""

import os
import sys

# Skip loading heavy ML models during testing for speed
os.environ["SKIP_EMBEDDER"] = "1"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
