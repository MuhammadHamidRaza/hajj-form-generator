import os
import io
import zipfile
import urllib.request
import concurrent.futures
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


@app.route("/generate-bulk", methods=["POST"])
def generate_bulk_pdfs():
    data: Dict[str, Any] = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request."}), 400

    serials: List[int] = data.get("serials", [])
    if not serials:
        return jsonify({"success": False, "message": "No serials provided."}), 400

    records: Optional[List[Dict[str, str]]] = load_excel_data()
    if records is None:
        return jsonify({"success": False, "message": "No Excel file loaded."}), 400

    pdf_filenames: List[Optional[str]] = [None] * len(serials)

    def process_one(i: int, serial: int) -> None:
        applicant: Optional[Dict[str, str]] = get_applicant(records, serial)
        if applicant is None:
            return
        pdf_filenames[i] = generate_pdf(applicant, serial_number=serial)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i, serial in enumerate(serials):
            futures.append(executor.submit(process_one, i, serial))
        concurrent.futures.wait(futures)

    generated_files: List[str] = [fn for fn in pdf_filenames if fn]
    if not generated_files:
        return jsonify(
            {"success": False, "message": "No PDFs could be generated."}
        ), 500

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fn in generated_files:
            fp = os.path.join(GENERATED_FOLDER, fn)
            if os.path.exists(fp):
                zf.write(fp, arcname=fn)

    zip_buffer.seek(0)
    zip_name: str = f"hajj_forms_{serials[0]}_to_{serials[-1]}.zip"

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=zip_name,
        mimetype="application/zip",
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
