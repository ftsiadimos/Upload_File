import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR.parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_CONFIG = {
    "UPLOAD_FOLDER": str(UPLOAD_FOLDER),
    "MAX_CONTENT_LENGTH": 500 * 1024 * 1024,
    "ALLOWED_EXTENSIONS": {
        "txt", "pdf", "png", "jpg", "jpeg", "gif", "zip", "csv", "xlsx", "docx", "pptx",
        "mp4", "avi", "mkv", "mp3", "wav", "flac", "html", "css", "js", "json", "xml", "yml",
        "yaml", "md", "log", "sql", "py", "java", "c", "cpp", "h", "hpp", "kdbx", "7z", "tar",
        "gz", "bz2", "xz", "iso", "dmg", "exe", "msi", "apk", "ipa", "jex"
    },
    "CATEGORIES": [
        "Documents",
        "Images",
        "Audio",
        "Video",
        "Archives",
        "Others",
    ],
    "PAGINATION_PER_CATEGORY": 5,
}


def _load_settings() -> dict:
    """Load settings from settings.json, falling back to defaults."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Merge with defaults so new keys don't break things
            merged = {**DEFAULT_CONFIG, **saved}
            # Merge sets properly
            if isinstance(saved.get("ALLOWED_EXTENSIONS"), (list, tuple)):
                merged["ALLOWED_EXTENSIONS"] = set(saved["ALLOWED_EXTENSIONS"])
            return merged
        except (json.JSONDecodeError, TypeError):
            pass
    return dict(DEFAULT_CONFIG)


def save_settings(settings: dict) -> None:
    """Save settings to settings.json."""
    serializable = {
        "UPLOAD_FOLDER": settings.get("UPLOAD_FOLDER", DEFAULT_CONFIG["UPLOAD_FOLDER"]),
        "MAX_CONTENT_LENGTH": settings.get("MAX_CONTENT_LENGTH", DEFAULT_CONFIG["MAX_CONTENT_LENGTH"]),
        "ALLOWED_EXTENSIONS": sorted(settings.get("ALLOWED_EXTENSIONS", DEFAULT_CONFIG["ALLOWED_EXTENSIONS"])),
        "CATEGORIES": settings.get("CATEGORIES", DEFAULT_CONFIG["CATEGORIES"]),
        "PAGINATION_PER_CATEGORY": settings.get("PAGINATION_PER_CATEGORY", DEFAULT_CONFIG["PAGINATION_PER_CATEGORY"]),
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


def reset_settings() -> None:
    """Reset settings to defaults by removing the settings file."""
    if SETTINGS_FILE.exists():
        SETTINGS_FILE.unlink()


class Config:
    _settings = _load_settings()

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "replace-this-with-a-secure-key")
    _saved_upload_folder = _settings["UPLOAD_FOLDER"]
    # If the saved path doesn't exist (e.g., Docker container with a different mount),
    # fall back to the default relative path so the app can create it.
    UPLOAD_FOLDER = _saved_upload_folder if Path(_saved_upload_folder).exists() else BASE_DIR.parent / "uploads"
    MAX_CONTENT_LENGTH = _settings["MAX_CONTENT_LENGTH"]
    ALLOWED_EXTENSIONS = _settings["ALLOWED_EXTENSIONS"]
    CATEGORIES = _settings["CATEGORIES"]
    PAGINATION_PER_CATEGORY = _settings["PAGINATION_PER_CATEGORY"]

