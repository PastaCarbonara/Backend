import uuid


def generate_unique_filename(filename: str):
    return filename + "-" + str(uuid.uuid4())
