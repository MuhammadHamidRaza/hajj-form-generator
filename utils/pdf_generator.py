import os
import traceback
import threading
from typing import Dict, Optional
from flask import render_template
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from config import PDF_CONFIG, GENERATED_FOLDER

_thread_local = threading.local()
_thread_playwright: dict = {}
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
]


def _clear_browser_tid(tid):
    entry = _thread_playwright.pop(tid, None)
    if entry:
        pw, browser, page = entry
        try:
            page.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def _get_browser_page():
    tid = threading.get_ident()
    entry = _thread_playwright.get(tid)
    if entry:
        pw, browser, page = entry
        try:
            page.title()
            return page
        except Exception:
            print(f"[PLAYWRIGHT] Page/browser disconnected, recreating...")
            _clear_browser_tid(tid)

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True, args=BROWSER_ARGS)
    page = browser.new_page()
    _thread_playwright[tid] = (pw, browser, page)
    return page


def generate_pdf(
    applicant: Dict[str, str],
    serial_number: int = 0,
    template_name: str = "pdf_template.html",
) -> Optional[str]:
    try:
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

        page = _get_browser_page()
        for attempt in range(2):
            try:
                page.set_content(html_content, wait_until="load", timeout=30000)
                break
            except PlaywrightTimeout:
                page.set_content(html_content, wait_until="commit", timeout=15000)
                break
            except Exception:
                if attempt == 0:
                    print(f"[PLAYWRIGHT] Page error on attempt {attempt}, recreating browser...")
                    tid = threading.get_ident()
                    _clear_browser_tid(tid)
                    page = _get_browser_page()
                else:
                    raise

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

        if os.path.exists(output_path):
            return sanitized_filename

        print(f"[PDF ERROR] File not created at {output_path}")
        return None

    except Exception as e:
        print(f"[PDF ERROR] {traceback.format_exc()}")
        return None
