import os

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
GENERATED_FOLDER: str = os.path.join(BASE_DIR, "generated")
TEMPLATES_FOLDER: str = os.path.join(BASE_DIR, "templates")
STATIC_FOLDER: str = os.path.join(BASE_DIR, "static")

DEFAULT_EXCEL: str = os.path.join(UPLOAD_FOLDER, "applicants.xlsx")

ALLOWED_EXTENSIONS: set = {"xlsx", "xls"}

MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

PDF_CONFIG: dict = {
    "width": "210mm",
    "height": "297mm",
    "margin_top": "15mm",
    "margin_bottom": "15mm",
    "margin_left": "12mm",
    "margin_right": "12mm",
    "print_background": True,
    "scale": 1,
}

SECTION_LABELS: dict = {
    "family": {"en": "Family Information", "ur": "\u062e\u0627\u0646\u062f\u0627\u0646\u06cc \u0645\u0639\u0644\u0648\u0645\u0627\u062a"},
    "applicant": {"en": "Applicant Information", "ur": "\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u06af\u0632\u0627\u0631 \u06a9\u06cc \u0645\u0639\u0644\u0648\u0645\u0627\u062a"},
    "contact": {"en": "Contact Information", "ur": "\u0631\u0627\u0628\u0637\u06c1 \u0645\u0639\u0644\u0648\u0645\u0627\u062a"},
    "mehram": {"en": "Mehram Information", "ur": "\u0645\u062d\u0631\u0645 \u06a9\u06cc \u0645\u0639\u0644\u0648\u0645\u0627\u062a"},
    "nominee": {"en": "Nominee Information", "ur": "\u0646\u0627\u0645\u0632\u062f \u0634\u062e\u0635 \u06a9\u06cc \u0645\u0639\u0644\u0648\u0645\u0627\u062a"},
    "bank": {"en": "Bank Information", "ur": "\u0628\u06cc\u0646\u06a9 \u0645\u0639\u0644\u0648\u0645\u0627\u062a"},
}

FIELD_LABELS: dict = {
    "Family Size": {"en": "Family Size", "ur": "\u062e\u0627\u0646\u062f\u0627\u0646 \u06a9\u0627 \u0633\u0627\u0626\u0632"},
    "Family Number": {"en": "Family Number", "ur": "\u062e\u0627\u0646\u062f\u0627\u0646 \u0646\u0645\u0628\u0631"},
    "Family Leader's Cnic Number": {"en": "Family Leader's CNIC Number", "ur": "\u062e\u0627\u0646\u062f\u0627\u0646 \u06a9\u06d2 \u0633\u0631\u0628\u0631\u0627\u06c1 \u06a9\u0627 \u0634\u0646\u0627\u062e\u062a\u06cc \u06a9\u0627\u0631\u0688 \u0646\u0645\u0628\u0631"},
    "Family Leader's Name": {"en": "Family Leader's Name", "ur": "\u062e\u0627\u0646\u062f\u0627\u0646 \u06a9\u06d2 \u0633\u0631\u0628\u0631\u0627\u06c1 \u06a9\u0627 \u0646\u0627\u0645"},
    "Applicant Type": {"en": "Applicant Type", "ur": "\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u06af\u0632\u0627\u0631 \u06a9\u06cc \u0642\u0633\u0645"},
    "Surname of Applicant": {"en": "Surname", "ur": "\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u06af\u0632\u0627\u0631 \u06a9\u0627 \u062e\u0627\u0646\u062f\u0627\u0646\u06cc \u0646\u0627\u0645"},
    "Given Name of Applicant": {"en": "Given Name", "ur": "\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u06af\u0632\u0627\u0631 \u06a9\u0627 \u0646\u0627\u0645"},
    "Father's / Husband's Name": {"en": "Father's / Husband's Name", "ur": "\u0648\u0627\u0644\u062f / \u0634\u0648\u06c1\u0631 \u06a9\u0627 \u0646\u0627\u0645"},
    "Gender": {"en": "Gender", "ur": "\u062c\u0646\u0633"},
    "Passport No.": {"en": "Passport Number", "ur": "\u067e\u0627\u0633\u067e\u0648\u0631\u0679 \u0646\u0645\u0628\u0631"},
    "Passport Date of Expiry": {"en": "Passport Expiry Date", "ur": "\u067e\u0627\u0633\u067e\u0648\u0631\u0679 \u06a9\u06cc \u0645\u06cc\u0627\u062f \u062e\u062a\u0645 \u06c1\u0648\u0646\u06d2 \u06a9\u06cc \u062a\u0627\u0631\u06cc\u062e"},
    "CNIC No.": {"en": "CNIC Number", "ur": "\u0634\u0646\u0627\u062e\u062a\u06cc \u06a9\u0627\u0631\u0688 \u0646\u0645\u0628\u0631"},
    "Date of Birth": {"en": "Date of Birth", "ur": "\u062a\u0627\u0631\u06cc\u062e \u067e\u06cc\u062f\u0627\u0626\u0634"},
    "Blood Group": {"en": "Blood Group", "ur": "\u0628\u0644\u0688 \u06af\u0631\u0648\u067e"},
    "Present Postal Address": {"en": "Present Postal Address", "ur": "\u0645\u0648\u062c\u0648\u062f\u06c1 \u0688\u0627\u06a9 \u06a9\u0627 \u067e\u062a\u06c1"},
    "Mobile Service Provider": {"en": "Mobile Service Provider", "ur": "\u0645\u0648\u0628\u0627\u0626\u0644 \u0633\u0631\u0648\u0633 \u0641\u0631\u0627\u06c1\u0645 \u06a9\u0631\u0646\u06d2 \u0648\u0627\u0644\u0627"},
    "Mobile No.": {"en": "Mobile Number", "ur": "\u0645\u0648\u0628\u0627\u0626\u0644 \u0646\u0645\u0628\u0631"},
    "Whatsapp Number": {"en": "WhatsApp Number", "ur": "\u0648\u0627\u0679\u0633 \u0627\u06cc\u067E \u0646\u0645\u0628\u0631"},
    "Mehram Name(In case of Female)": {"en": "Mehram Name (In case of Female)", "ur": "\u0645\u062d\u0631\u0645 \u06a9\u0627 \u0646\u0627\u0645 (\u062e\u0648\u0627\u062a\u06cc\u0646 \u06a9\u06cc \u0635\u0648\u0631\u062a \u0645\u06cc\u06ba)"},
    "Relationship with Mehram": {"en": "Relationship with Mehram", "ur": "\u0645\u062d\u0631\u0645 \u0633\u06d2 \u0631\u0634\u062a\u06c1"},
    "Nominee Name": {"en": "Nominee Name", "ur": "\u0646\u0627\u0645\u0632\u062f \u0634\u062e\u0635 \u06a9\u0627 \u0646\u0627\u0645"},
    "Nominee CNIC No.": {"en": "Nominee CNIC Number", "ur": "\u0646\u0627\u0645\u0632\u062f \u0634\u062e\u0635 \u06a9\u0627 \u0634\u0646\u0627\u062e\u062a\u06cc \u06a9\u0627\u0631\u0688 \u0646\u0645\u0628\u0631"},
    "Relationship with Applicant": {"en": "Relationship with Applicant", "ur": "\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u06af\u0632\u0627\u0631 \u0633\u06d2 \u0631\u0634\u062a\u06c1"},
    "Nominee Mobile No.": {"en": "Nominee Mobile Number", "ur": "\u0646\u0627\u0645\u0632\u062f \u0634\u062e\u0635 \u06a9\u0627 \u0645\u0648\u0628\u0627\u0626\u0644 \u0646\u0645\u0628\u0631"},
    "Bank Account No. (IBAN)": {"en": "Bank Account (IBAN)", "ur": "\u0628\u06cc\u0646\u06a9 \u0627\u06a9\u0627\u0624\u0646\u0679 \u0646\u0645\u0628\u0631 (IBAN)"},
    "Account Title": {"en": "Account Title", "ur": "\u0627\u06a9\u0627\u0624\u0646\u0679 \u06a9\u0627 \u0639\u0646\u0648\u0627\u0646"},
}

SECTION_FIELDS: dict = {
    "family": [
        "Family Size",
        "Family Number",
        "Family Leader's Cnic Number",
        "Family Leader's Name",
    ],
    "applicant": [
        "Applicant Type",
        "Surname of Applicant",
        "Given Name of Applicant",
        "Father's / Husband's Name",
        "Gender",
        "Passport No.",
        "Passport Date of Expiry",
        "CNIC No.",
        "Date of Birth",
        "Blood Group",
    ],
    "contact": [
        "Present Postal Address",
        "Mobile Service Provider",
        "Mobile No.",
        "Whatsapp Number",
    ],
    "mehram": [
        "Mehram Name(In case of Female)",
        "Relationship with Mehram",
    ],
    "nominee": [
        "Nominee Name",
        "Nominee CNIC No.",
        "Relationship with Applicant",
        "Nominee Mobile No.",
    ],
    "bank": [
        "Bank Account No. (IBAN)",
        "Account Title",
    ],
}

SECRET_KEY: str = "hajj-form-generator-secret-key-2024"
