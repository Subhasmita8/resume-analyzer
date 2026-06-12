"""
app.py
------
Flask application entry point.

Exposes:
    POST /analyze  – accepts a resume file + job description, returns JSON analysis.
    GET  /health   – simple liveness check.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.parser import parse_resume
from utils.matcher import compute_match

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend on a different origin (e.g., file:// or localhost:5500)

# Max upload size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """Liveness probe."""
    return jsonify({"status": "ok"}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze a resume against a job description.

    Form fields:
        resume  (file)   – PDF or DOCX resume.
        job_description (str) – Plain-text job description.

    Returns:
        200 JSON:
            score             (float)  0-100 match percentage
            missing_skills    (list)   keywords in JD absent from resume
            suggestions       (list)   actionable improvement tips
            matching_keywords (list)   keywords present in both documents
        400 JSON: { "error": "<message>" }
        500 JSON: { "error": "<message>" }
    """
    # --- Validate resume file ---
    if "resume" not in request.files:
        return jsonify({"error": "No resume file provided. Please upload a PDF or DOCX."}), 400

    resume_file = request.files["resume"]

    if resume_file.filename == "":
        return jsonify({"error": "Resume filename is empty."}), 400

    if not _allowed_file(resume_file.filename):
        return jsonify(
            {"error": f"File type not supported: '{resume_file.filename}'. Upload PDF or DOCX."}
        ), 400

    # --- Validate job description ---
    job_description = request.form.get("job_description", "").strip()
    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    if len(job_description) < 50:
        return jsonify(
            {"error": "Job description is too short. Please provide at least 50 characters."}
        ), 400

    # --- Parse resume ---
    try:
        file_bytes = resume_file.read()
        resume_text = parse_resume(file_bytes, resume_file.filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # --- Run analysis ---
    try:
        result = compute_match(resume_text, job_description)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.exception("Unexpected error during analysis")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500

    return jsonify(result), 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(413)
def file_too_large(_):
    return jsonify({"error": "File too large. Maximum allowed size is 5 MB."}), 413


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"error": "Method not allowed."}), 405


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
