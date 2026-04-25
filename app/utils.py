import json
import os
from pathlib import Path
from typing import List

from .config import Config


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def list_uploaded_files(upload_folder: str) -> List[str]:
    files: List[str] = []
    for root, _, filenames in os.walk(upload_folder):
        for filename in filenames:
            if filename.startswith("."):
                continue
            relative_path = Path(root).relative_to(upload_folder) / filename
            files.append(str(relative_path).replace("\\", "/"))
    return sorted(files)


def get_file_path(upload_folder: str, *path_segments: str) -> Path:
    return Path(upload_folder).joinpath(*path_segments)


def load_custom_categories(upload_folder: str) -> List[str]:
    path = Path(upload_folder) / ".categories.json"
    try:
        with open(path) as f:
            data = json.load(f)
            return [str(c) for c in data if isinstance(c, str)] if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_custom_categories(upload_folder: str, categories: List[str]) -> None:
    path = Path(upload_folder) / ".categories.json"
    with open(path, "w") as f:
        json.dump(categories, f)
