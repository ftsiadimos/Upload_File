import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR.parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif", "zip", "csv", "xlsx", "docx", "pptx",
    "mp4", "avi", "mkv", "mp3", "wav", "flac", "html", "css", "js", "json", "xml", "yml",
    "yaml", "md", "log", "sql", "py", "java", "c", "cpp", "h", "hpp", "kdbx", "7z", "tar",
    "gz", "bz2", "xz", "iso", "dmg", "exe", "msi", "apk", "ipa"
}

CATEGORIES = [
    "Documents",
    "Images",
    "Audio",
    "Video",
    "Archives",
    "Others",
]


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "replace-this-with-a-secure-key")
    UPLOAD_FOLDER = str(UPLOAD_FOLDER)
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
    CATEGORIES = CATEGORIES

