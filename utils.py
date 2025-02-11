"""
Utility functions used across the project.
"""

import os

def safe_mkdir(directory):
    """Create a directory if it does not already exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
