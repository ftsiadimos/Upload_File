import os
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from .config import Config
from .utils import allowed_file, format_bytes, get_disk_usage, get_file_path, list_uploaded_files, load_custom_categories, save_custom_categories

upload_bp = Blueprint("upload", __name__)

VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"


@upload_bp.route("/about", methods=["GET"])
def about():
    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    return render_template("about.html", app_version=version)


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
    disk = get_disk_usage(Config.UPLOAD_FOLDER)

    return render_template(
        "upload.html",
        grouped_files=grouped_files,
        sidebar_grouped=sidebar_grouped,
        categories=["All"] + all_categories + ["Uncategorized"],
        custom_categories=custom_categories,
        selected_category=selected_category,
        search_query=search_query,
        app_version=version,
        disk_usage=disk,
        format_bytes=format_bytes,
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


@upload_bp.route("/upload_folder", methods=["POST"])
def upload_folder():
    if "folder_files" not in request.files:
        flash("No folder selected")
        return redirect(url_for("upload.index"))

    files = request.files.getlist("folder_files")
    if not files or all(f.filename == "" for f in files):
        flash("No files in folder")
        return redirect(url_for("upload.index"))

    custom_categories = load_custom_categories(Config.UPLOAD_FOLDER)
    all_categories = Config.CATEGORIES + [c for c in custom_categories if c not in Config.CATEGORIES]
    category = request.form.get("category", "Others")
    if category not in all_categories:
        category = "Others"

    category_folder = get_file_path(Config.UPLOAD_FOLDER, category)
    category_folder.mkdir(parents=True, exist_ok=True)

    # Create a temporary directory to reconstruct folder structure
    import tempfile
    import zipfile

    temp_dir = tempfile.mkdtemp(prefix="folder_upload_")
    try:
        for file in files:
            if not file.filename:
                continue
            # The filename contains the relative path within the folder
            safe_filename = _safe_file_path(file.filename)
            if not safe_filename:
                continue
            dest_path = Path(temp_dir) / safe_filename
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(dest_path)

        # Create ZIP archive
        zip_filename = secure_filename(f"{category}_folder.zip")
        zip_path = category_folder / zip_filename

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, filenames in os.walk(temp_dir):
                for fname in filenames:
                    file_path = Path(root) / fname
                    arcname = str(file_path.relative_to(temp_dir))
                    zf.write(file_path, arcname)

        flash(f"Folder uploaded successfully: {category}/{zip_filename}")
    finally:
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    return redirect(url_for("upload.index"))


@upload_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    safe_filename = _safe_file_path(filename)
    return send_from_directory(Config.UPLOAD_FOLDER, safe_filename)


@upload_bp.route("/download/<path:filename>")
def download_file(filename):
    safe_filename = _safe_file_path(filename)
    return send_from_directory(Config.UPLOAD_FOLDER, safe_filename, as_attachment=True)


@upload_bp.route("/change-category/<path:filename>", methods=["POST"])
def change_category(filename):
    safe_name = _safe_file_path(filename)
    file_path = get_file_path(Config.UPLOAD_FOLDER, safe_name)

    if not file_path.exists():
        flash(f"File not found: {safe_name}")
        return redirect(url_for("upload.index"))

    new_category = request.form.get("category", "").strip()
    custom_categories = load_custom_categories(Config.UPLOAD_FOLDER)
    all_categories = Config.CATEGORIES + [c for c in custom_categories if c not in Config.CATEGORIES]

    if not new_category or new_category not in all_categories:
        flash("Invalid category selected.")
        return redirect(url_for("upload.index"))

    # Get the original file name (last part of the path)
    original_filename = Path(safe_name).name
    new_path = get_file_path(Config.UPLOAD_FOLDER, new_category, original_filename)

    # Ensure the destination category folder exists
    new_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if new_path.exists():
            flash(f"A file with the same name already exists in '{new_category}'.")
            return redirect(url_for("upload.index"))

        file_path.rename(new_path)
        flash(f"Moved to '{new_category}': {original_filename}")
    except Exception as e:
        flash(f"Error moving file: {e}")

    return redirect(url_for("upload.index"))


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


def render_error_page(code, title, message):
    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    return render_template("error.html", code=code, title=title, message=message), code


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return render_error_page(400, "Bad Request", "The request could not be understood by the server.")

    @app.errorhandler(403)
    def forbidden(error):
        return render_error_page(403, "Forbidden", "You don't have permission to access this resource.")

    @app.errorhandler(404)
    def page_not_found(error):
        return render_error_page(404, "Page Not Found", "The page you were looking for doesn't exist.")

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_error_page(405, "Method Not Allowed", "The requested method is not allowed for this URL.")

    @app.errorhandler(408)
    def request_timeout(error):
        return render_error_page(408, "Request Timeout", "The request took too long to complete.")

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_error_page(413, "Payload Too Large", "The uploaded file is too large. Maximum size is 500 MB.")

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_error_page(500, "Server Error", "An internal server error occurred. Please try again later.")
