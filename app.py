import os
import io
import uuid
import zipfile
import urllib.request
import traceback
import threading
from typing import Dict, Optional, List, Any
from flask import Flask, render_template, request, jsonify, send_file
from config import (
    UPLOAD_FOLDER,
    GENERATED_FOLDER,
    DEFAULT_EXCEL,
    MAX_CONTENT_LENGTH,
    SECRET_KEY,
    FIELD_LABELS,
    SECTION_LABELS,
    SECTION_FIELDS,
)
from utils.excel_reader import load_excel, get_applicant, get_total_applicants, validate_excel_columns
from utils.pdf_generator import generate_pdf

app: Flask = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SECRET_KEY"] = SECRET_KEY

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

TASKS: Dict[str, dict] = {}
TASKS_LOCK = threading.Lock()

EXCEL_SOURCE_URL: str = (
    "https://docs.google.com/spreadsheets/d/"
    "1SDl4lMbuwosOrxDqwou-C0DSYvpKB11HLV9OEANHEkc/export?format=xlsx"
)


def fetch_excel_from_url() -> bool:
    try:
        req = urllib.request.Request(
            EXCEL_SOURCE_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(DEFAULT_EXCEL, "wb") as f:
                f.write(response.read())
        if not validate_excel_columns(DEFAULT_EXCEL):
            os.remove(DEFAULT_EXCEL)
            return False
        return True
    except Exception:
        return False


def load_excel_data() -> Optional[List[Dict[str, str]]]:
    if os.path.exists(DEFAULT_EXCEL):
        try:
            return load_excel(DEFAULT_EXCEL)
        except Exception:
            return None
    return None


@app.route("/")
def index():
    records: Optional[List[Dict[str, str]]] = load_excel_data()
    total: int = get_total_applicants(records) if records else 0
    excel_loaded: bool = records is not None
    return render_template(
        "index.html",
        total_applicants=total,
        excel_loaded=excel_loaded,
    )


@app.route("/fetch", methods=["POST"])
def fetch_excel():
    success: bool = fetch_excel_from_url()
    if not success:
        return jsonify(
            {"success": False, "message": "Failed to fetch Excel from source."}
        ), 400
    records: List[Dict[str, str]] = load_excel(DEFAULT_EXCEL)
    total: int = get_total_applicants(records)
    return jsonify(
        {
            "success": True,
            "message": f"Excel loaded successfully. {total} applicant(s) found.",
            "total": total,
        }
    )


@app.route("/preview", methods=["POST"])
def preview_applicant():
    data: Dict[str, Any] = request.get_json()
    if not data or "serial_number" not in data:
        return jsonify({"success": False, "message": "Serial number required."}), 400

    try:
        serial_number: int = int(data["serial_number"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid serial number."}), 400

    records: Optional[List[Dict[str, str]]] = load_excel_data()
    if records is None:
        return jsonify(
            {"success": False, "message": "No Excel file loaded."}
        ), 400

    applicant: Optional[Dict[str, str]] = get_applicant(records, serial_number)
    if applicant is None:
        return jsonify(
            {
                "success": False,
                "message": f"Applicant with serial number {serial_number} not found.",
            }
        ), 404

    html: str = render_template(
        "preview.html",
        applicant=applicant,
        serial_number=serial_number,
        field_labels=FIELD_LABELS,
        section_labels=SECTION_LABELS,
        section_fields=SECTION_FIELDS,
    )

    return jsonify({"success": True, "html": html})


@app.route("/generate", methods=["POST"])
def generate_applicant_pdf():
    data: Dict[str, Any] = request.get_json()
    if not data or "serial_number" not in data:
        return jsonify({"success": False, "message": "Serial number required."}), 400

    try:
        serial_number: int = int(data["serial_number"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid serial number."}), 400

    records: Optional[List[Dict[str, str]]] = load_excel_data()
    if records is None:
        return jsonify(
            {"success": False, "message": "No Excel file loaded."}
        ), 400

    applicant: Optional[Dict[str, str]] = get_applicant(records, serial_number)
    if applicant is None:
        return jsonify(
            {
                "success": False,
                "message": f"Applicant with serial number {serial_number} not found.",
            }
        ), 404

    pdf_filename: Optional[str] = generate_pdf(applicant, serial_number=serial_number)
    if pdf_filename is None:
        return jsonify(
            {"success": False, "message": "Failed to generate PDF."}
        ), 500

    given_name: str = applicant.get("Given Name of Applicant", "")
    surname: str = applicant.get("Surname of Applicant", "")
    full_name: str = f"{given_name} {surname}".strip()

    return jsonify(
        {
            "success": True,
            "message": f"PDF generated successfully for {full_name}.",
            "filename": pdf_filename,
        }
    )


@app.route("/download/<filename>")
def download_pdf(filename: str):
    filepath: str = os.path.join(GENERATED_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "message": "File not found."}), 404
    return send_file(filepath, as_attachment=True, mimetype="application/pdf")


def _background_generate(task_id: str) -> None:
    task = TASKS.get(task_id)
    if not task:
        return

    with app.app_context():
        records: Optional[List[Dict[str, str]]] = load_excel_data()
        if records is None:
            task["status"] = "error"
            task["message"] = "No Excel data loaded."
            return

        serials: List[int] = task["serials"]
        generated_files: List[str] = []
        failed: List[int] = []

        for i, serial in enumerate(serials):
            task["progress"] = i
            task["status"] = "processing"
            applicant: Optional[Dict[str, str]] = get_applicant(records, serial)
            if applicant is None:
                failed.append(serial)
                continue
            pdf_fn: Optional[str] = generate_pdf(applicant, serial_number=serial)
            if pdf_fn:
                generated_files.append(pdf_fn)
            else:
                failed.append(serial)

        if not generated_files:
            task["status"] = "error"
            err_msg = "No PDFs could be generated."
            if failed:
                err_msg += f" Failed serials: {failed[:20]}"
                if len(failed) > 20:
                    err_msg += f" ... and {len(failed)-20} more"
            task["message"] = err_msg
            return

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for fn in generated_files:
                fp = os.path.join(GENERATED_FOLDER, fn)
                if os.path.exists(fp):
                    zf.write(fp, arcname=fn)

        zip_filename = f"task_{task_id}.zip"
        zip_path = os.path.join(GENERATED_FOLDER, zip_filename)
        with open(zip_path, "wb") as f:
            f.write(zip_buffer.getvalue())

        task["status"] = "done"
        task["progress"] = len(serials)
        task["download_url"] = f"/download-task/{zip_filename}"
        task["zip_filename"] = zip_filename


@app.route("/generate-bulk", methods=["POST"])
def generate_bulk_pdfs():
    data: Dict[str, Any] = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request."}), 400

    serials: List[int] = data.get("serials", [])
    if not serials:
        return jsonify({"success": False, "message": "No serials provided."}), 400

    task_id: str = str(uuid.uuid4())
    task: Dict[str, Any] = {
        "id": task_id,
        "status": "queued",
        "progress": 0,
        "total": len(serials),
        "serials": serials,
        "download_url": None,
        "zip_filename": None,
        "message": None,
    }
    with TASKS_LOCK:
        TASKS[task_id] = task

    thread = threading.Thread(
        target=_background_generate, args=(task_id,), daemon=True
    )
    thread.start()

    return jsonify(
        {
            "success": True,
            "async": True,
            "task_id": task_id,
            "total": len(serials),
        }
    )


@app.route("/task-status/<task_id>")
def task_status(task_id: str):
    with TASKS_LOCK:
        task: Optional[Dict[str, Any]] = TASKS.get(task_id)
    if not task:
        return jsonify({"success": False, "message": "Task not found."}), 404
    return jsonify(
        {
            "success": True,
            "status": task["status"],
            "progress": task["progress"],
            "total": task["total"],
            "download_url": task.get("download_url"),
            "message": task.get("message"),
        }
    )


@app.route("/download-task/<filename>")
def download_task_zip(filename: str):
    filepath: str = os.path.join(GENERATED_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "message": "File not found."}), 404
    return send_file(
        filepath, as_attachment=True, download_name="hajj_forms.zip", mimetype="application/zip"
    )


@app.route("/status")
def check_status():
    records: Optional[List[Dict[str, str]]] = load_excel_data()
    total: int = get_total_applicants(records) if records else 0
    excel_loaded: bool = records is not None
    return jsonify(
        {
            "excel_loaded": excel_loaded,
            "total_applicants": total,
        }
    )


if __name__ == "__main__":
    import os
    port: int = int(os.environ.get("PORT", 5000))
    fetch_excel_from_url()
    app.run(host="0.0.0.0", port=port, debug=False)
