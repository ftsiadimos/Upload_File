import os
from pathlib import Path
from typing import List

from .config import Config


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def list_uploaded_files(upload_folder: str) -> List[str]:
    try:
        return sorted(os.listdir(upload_folder))
    except FileNotFoundError:
        return []


def get_file_path(upload_folder: str, filename: str) -> Path:
    return Path(upload_folder) / filename
