"""
Image utility functions
"""


import uuid


def generate_unique_filename(filename: str):
    """
    Generate random file name with give filename using uuid4
    """
    filename, extension = filename.split(".")
    return f"{filename}-{str(uuid.uuid4())}.{extension}"
