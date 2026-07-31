"""
pytest configuration
Fixes Python path for imports
"""

import sys
from pathlib import Path

# Add DataVault root to Python path
root = Path(__file__).parent
sys.path.insert(0, str(src_path))
