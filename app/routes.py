import os
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from .config import Config
from .utils import allowed_file, get_file_path, list_uploaded_files

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/", methods=["GET"])
def index():
    search_query = request.args.get("q", "").strip()
    files = list_uploaded_files(Config.UPLOAD_FOLDER)

    if search_query:
        files = [f for f in files if search_query.lower() in f.lower()]

    return render_template("upload.html", files=files, search_query=search_query)


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

    filename = secure_filename(file.filename)
    file_path = get_file_path(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)

    flash(f"File uploaded successfully: {filename}")
    return redirect(url_for("upload.index"))


@upload_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@upload_bp.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    safe_name = secure_filename(filename)
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
