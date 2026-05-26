import os
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from .config import Config
from .utils import allowed_file, get_file_path, list_uploaded_files, load_custom_categories, save_custom_categories

upload_bp = Blueprint("upload", __name__)

VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"


def _group_files_by_category(files, all_categories):
    grouped = {category: [] for category in all_categories}
    grouped["Uncategorized"] = []

    for file_entry in files:
        file_path = file_entry["path"]
        first_part = file_path.split("/", 1)[0]
        if first_part in all_categories:
            grouped[first_part].append(file_entry)
        else:
            grouped["Uncategorized"].append(file_entry)

    return grouped


@upload_bp.route("/", methods=["GET"])
def index():
    search_query = request.args.get("q", "").strip()
    selected_category = request.args.get("category", "All")
    files = list_uploaded_files(Config.UPLOAD_FOLDER)
    custom_categories = load_custom_categories(Config.UPLOAD_FOLDER)
    all_categories = Config.CATEGORIES + [c for c in custom_categories if c not in Config.CATEGORIES]

    # sidebar always shows unfiltered counts
    sidebar_grouped = _group_files_by_category(files, all_categories)

    if search_query:
        files = [f for f in files if search_query.lower() in f["path"].lower()]

    grouped_files = _group_files_by_category(files, all_categories)

    if selected_category != "All":
        grouped_files = {
            selected_category: grouped_files.get(selected_category, [])
        }

    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"

    return render_template(
        "upload.html",
        grouped_files=grouped_files,
        sidebar_grouped=sidebar_grouped,
        categories=["All"] + all_categories + ["Uncategorized"],
        custom_categories=custom_categories,
        selected_category=selected_category,
        search_query=search_query,
        app_version=version,
    )


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for("upload.index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("upload.index"))

    if not allowed_file(file.filename):
        flash(f"Disallowed file type: {file.filename}")
        return redirect(url_for("upload.index"))

    custom_categories = load_custom_categories(Config.UPLOAD_FOLDER)
    all_categories = Config.CATEGORIES + [c for c in custom_categories if c not in Config.CATEGORIES]
    category = request.form.get("category", "Others")
    if category not in all_categories:
        category = "Others"

    filename = secure_filename(file.filename)
    category_folder = get_file_path(Config.UPLOAD_FOLDER, category)
    category_folder.mkdir(parents=True, exist_ok=True)

    file_path = get_file_path(Config.UPLOAD_FOLDER, category, filename)
    file.save(file_path)

    flash(f"File uploaded successfully: {category}/{filename}")
    return redirect(url_for("upload.index"))


def _safe_file_path(filename: str) -> str:
    normalized = Path(filename).as_posix().lstrip("./")
    safe_parts = [secure_filename(part) for part in normalized.split("/") if part]
    return "/".join(safe_parts)


@upload_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    safe_filename = _safe_file_path(filename)
    return send_from_directory(Config.UPLOAD_FOLDER, safe_filename)


@upload_bp.route("/download/<path:filename>")
def download_file(filename):
    safe_filename = _safe_file_path(filename)
    return send_from_directory(Config.UPLOAD_FOLDER, safe_filename, as_attachment=True)


@upload_bp.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    safe_name = _safe_file_path(filename)
    file_path = get_file_path(Config.UPLOAD_FOLDER, safe_name)

    if not file_path.exists():
        flash(f"File not found: {safe_name}")
        return redirect(url_for("upload.index"))

    try:
        file_path.unlink()
        flash(f"File deleted: {safe_name}")
    except Exception as e:
        flash(f"Error deleting file {safe_name}: {e}")

    return redirect(url_for("upload.index"))


@upload_bp.route("/api/total", methods=["GET"])
def files_total():
    total = len(list_uploaded_files(Config.UPLOAD_FOLDER))
    return {"total": total}


@upload_bp.route("/category/add", methods=["POST"])
def add_category():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Category name cannot be empty.")
        return redirect(url_for("upload.index"))

    safe_name = secure_filename(name)
    if not safe_name or safe_name.lower() in ("all", "uncategorized"):
        flash("Invalid or reserved category name.")
        return redirect(url_for("upload.index"))

    if safe_name in Config.CATEGORIES:
        flash(f"'{safe_name}' is already a built-in category.")
        return redirect(url_for("upload.index"))

    custom_categories = load_custom_categories(Config.UPLOAD_FOLDER)
    if safe_name in custom_categories:
        flash(f"Category already exists: {safe_name}")
        return redirect(url_for("upload.index"))

    custom_categories.append(safe_name)
    save_custom_categories(Config.UPLOAD_FOLDER, custom_categories)
    flash(f"Category added: {safe_name}")
    return redirect(url_for("upload.index"))


@upload_bp.route("/category/delete/<name>", methods=["POST"])
def delete_category(name):
    safe_name = secure_filename(name)
    if safe_name in Config.CATEGORIES:
        flash(f"Cannot delete built-in category: {safe_name}")
        return redirect(url_for("upload.index"))

    custom_categories = load_custom_categories(Config.UPLOAD_FOLDER)
    if safe_name not in custom_categories:
        flash(f"Category not found: {safe_name}")
        return redirect(url_for("upload.index"))

    category_folder = get_file_path(Config.UPLOAD_FOLDER, safe_name)
    if category_folder.exists() and any(category_folder.iterdir()):
        flash(f"Cannot delete '{safe_name}': it still contains files.")
        return redirect(url_for("upload.index"))

    custom_categories.remove(safe_name)
    save_custom_categories(Config.UPLOAD_FOLDER, custom_categories)
    if category_folder.exists():
        category_folder.rmdir()

    flash(f"Category deleted: {safe_name}")
    return redirect(url_for("upload.index"))


@upload_bp.app_errorhandler(413)
def request_entity_too_large(error):
    flash("File is too large. Maximum size is 100 MB.")
    return redirect(url_for("upload.index"))


@upload_bp.app_errorhandler(404)
def page_not_found(error):
    flash("Page not found.")
    return redirect(url_for("upload.index"))


@upload_bp.app_errorhandler(500)
def internal_server_error(error):
    flash("An internal server error occurred.")
    return redirect(url_for("upload.index"))


@upload_bp.app_errorhandler(400)
def bad_request(error):
    flash("Bad request.")
    return redirect(url_for("upload.index"))


@upload_bp.app_errorhandler(403)
def forbidden(error):
    flash("Forbidden.")
    return redirect(url_for("upload.index"))


@upload_bp.app_errorhandler(405)
def method_not_allowed(error):
    flash("Method not allowed.")
    return redirect(url_for("upload.index"))


@upload_bp.app_errorhandler(408)
def request_timeout(error):
    flash("Request timeout.")
    return redirect(url_for("upload.index"))
