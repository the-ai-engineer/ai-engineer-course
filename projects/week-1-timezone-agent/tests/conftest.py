"""Pytest configuration."""

import sys
from pathlib import Path

# Add project root to path so we can import agent.py
sys.path.insert(0, str(Path(__file__).parent.parent))
