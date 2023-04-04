import uuid


def generate_unique_filename(filename: str):
    filename, extension = filename.split(".")
    return f"{filename}-{str(uuid.uuid4())}.{extension}"
