import os
from typing import Dict, Optional
from flask import render_template
from playwright.sync_api import sync_playwright
from config import PDF_CONFIG, GENERATED_FOLDER


def generate_pdf(
    applicant: Dict[str, str],
    serial_number: int = 0,
    template_name: str = "pdf_template.html",
) -> Optional[str]:
    surname: str = applicant.get("Surname of Applicant", "")
    given_name: str = applicant.get("Given Name of Applicant", "")
    full_name: str = f"{given_name} {surname}".strip()
    if not full_name:
        full_name = "Applicant"

    passport: str = applicant.get("Passport No.", "")
    if passport:
        filename: str = f"{full_name}_{passport}.pdf"
    else:
        filename: str = f"{full_name}.pdf"

    sanitized_filename: str = "".join(
        c for c in filename if c.isalnum() or c in "._- "
    ).strip()
    if not sanitized_filename:
        sanitized_filename = "applicant.pdf"

    output_path: str = os.path.join(GENERATED_FOLDER, sanitized_filename)

    from config import FIELD_LABELS, SECTION_LABELS, SECTION_FIELDS

    html_content: str = render_template(
        template_name,
        applicant=applicant,
        serial_number=serial_number,
        field_labels=FIELD_LABELS,
        section_labels=SECTION_LABELS,
        section_fields=SECTION_FIELDS,
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")

        page.pdf(
            path=output_path,
            format="A4",
            margin={
                "top": PDF_CONFIG["margin_top"],
                "bottom": PDF_CONFIG["margin_bottom"],
                "left": PDF_CONFIG["margin_left"],
                "right": PDF_CONFIG["margin_right"],
            },
            print_background=PDF_CONFIG["print_background"],
            scale=PDF_CONFIG["scale"],
            display_header_footer=False,
        )

        browser.close()

    if os.path.exists(output_path):
        return sanitized_filename

    return None
