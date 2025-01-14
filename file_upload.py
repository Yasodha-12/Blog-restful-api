import os
from werkzeug.utils import secure_filename
from flask import request, jsonify

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def setup_file_uploads(app):
    @app.route("/upload/<path:folder>", methods=["POST"])
    def upload_file(folder):
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        filename = secure_filename(file.filename)
        upload_folder = os.path.join(app.config["UPLOAD_FOLDER"], folder)
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        return jsonify({"message": "File uploaded successfully", "path": file_path}), 201
