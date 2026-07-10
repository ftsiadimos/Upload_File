import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from .config import Config


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def list_uploaded_files(upload_folder: str) -> List[dict]:
    files: List[dict] = []
    for root, _, filenames in os.walk(upload_folder):
        for filename in filenames:
            if filename.startswith("."):
                continue
            file_path = Path(root) / filename
            relative_path = file_path.relative_to(upload_folder).as_posix()
            modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            files.append({
                "path": relative_path,
                "date": modified_time.strftime("%Y-%m-%d %H:%M"),
            })
    return sorted(files, key=lambda entry: entry["path"])


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


def get_disk_usage(upload_folder: str) -> dict:
    """Return disk usage info for the partition containing upload_folder."""
    usage = shutil.disk_usage(upload_folder)
    total = usage.total
    used = usage.used
    free = usage.free
    percent = (used / total * 100) if total else 0
    return {
        "total": total,
        "used": used,
        "free": free,
        "percent": round(percent, 1),
    }


def format_bytes(size: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"):
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} YB"
