"""
Image utility functions
"""


import uuid


def generate_unique_filename(filename: str):
    """
    Generate random file name using uuid4
    """
    filename = filename.split(".")[0]
    return f"{str(uuid.uuid4())}.webp"
