import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file_locally(file: UploadFile) -> str:
    """Saves the uploaded file to disk with a unique filename and returns that filename."""
    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return unique_filename


def delete_file_locally(filename: str) -> None:
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)