# Hajj Form Generator

A professional web application to generate Hajj application PDF forms from Excel data.

## Features

- Upload Excel files containing applicant data
- Preview applicant information before generating PDF
- Generate beautiful, print-ready A4 PDF forms
- Bilingual labels (English + Urdu)
- Modern, responsive UI with glassmorphism design

## Requirements

- Python 3.8+
- Google Chrome / Chromium (for Playwright PDF generation)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd hajj-form-generator
```

### 2. Create virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install chromium
```

### 5. Prepare Excel file

Place your Excel file named `applicants.xlsx` in the `uploads/` directory.

The Excel file must contain the following columns:
- Family Size
- Family Number
- Family Leader's Cnic Number
- Family Leader's Name
- Applicant Type
- Surname of Applicant
- Given Name of Applicant
- Father's / Husband's Name
- Gender
- Passport No.
- Passport Date of Expiry
- CNIC No.
- Date of Birth
- Blood Group
- Present Postal Address
- Mobile Service Provider
- Mobile No.
- Whatsapp Number
- Mehram Name(In case of Female)
- Relationship with Mehram
- Nominee Name
- Nominee CNIC No.
- Relationship with Applicant
- Nominee Mobile No.
- Bank Account No. (IBAN)
- Account Title

### 6. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Open `http://localhost:5000` in your browser
2. The application will automatically detect `uploads/applicants.xlsx` if present
3. Alternatively, upload an Excel file using the upload area
4. Enter a serial number (row number) of the applicant
5. Click **Preview** to view applicant information
6. Click **Generate PDF** to create and download the PDF form

## Deployment

### Using Gunicorn (Linux/macOS)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Waitress (Windows)

```bash
pip install waitress
waitress-serve --port=8000 app:app
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

RUN mkdir -p uploads generated

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Project Structure

```
hajj-form-generator/
├── app.py                  # Flask application
├── config.py               # Configuration and field mappings
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
├── templates/
│   ├── index.html          # Home page
│   ├── preview.html        # Preview template
│   └── pdf_template.html   # PDF template
├── static/
│   ├── css/
│   │   └── style.css       # Stylesheet
│   └── js/
│       └── app.js          # Frontend logic
├── utils/
│   ├── __init__.py
│   ├── excel_reader.py     # Excel file reader
│   ├── pdf_generator.py    # PDF generation with Playwright
│   └── helpers.py          # Utility functions
├── uploads/                # Excel file upload directory
└── generated/              # Generated PDF files
```

## Notes

- Empty fields in Excel are displayed as blank (never "None", "NaN", or "null")
- Field labels are bilingual (English + Urdu)
- Values remain exactly as they appear in Excel (not translated)
- PDFs are A4 format, print-ready, with no browser headers or footers
