from typing import Dict, List, Optional, Any
import pandas as pd
import re
from utils.helpers import clean_row


REQUIRED_COLUMNS: List[str] = [
    "Family Size",
    "Family Number",
    "Family Leader's Cnic Number",
    "Family Leader's Name",
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
    "Present Postal Address",
    "Mobile Service Provider",
    "Mobile No.",
    "Whatsapp Number",
    "Mehram Name(In case of Female)",
    "Relationship with Mehram",
    "Nominee Name",
    "Nominee CNIC No.",
    "Relationship with Applicant",
    "Nominee Mobile No.",
    "Bank Account No. (IBAN)",
    "Account Title",
]


KNOWN_TYPOS: Dict[str, str] = {
    "Moile Servie Provider": "Mobile Service Provider",
    "Mobile Servie Provider": "Mobile Service Provider",
    "Moile Service Provider": "Mobile Service Provider",
}


def _normalize(name: str) -> str:
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    return name


def _fuzzy_match(actual_cols: List[str], required: str) -> Optional[str]:
    normalized_req = _normalize(required).lower().replace("'", "").replace("/", " ").replace("(", "").replace(")", "")
    normalized_req = re.sub(r'\s+', ' ', normalized_req).strip()

    best_match: Optional[str] = None
    best_score: int = 0

    for actual in actual_cols:
        normalized_actual = _normalize(actual).lower().replace("'", "").replace("/", " ").replace("(", "").replace(")", "")
        normalized_actual = re.sub(r'\s+', ' ', normalized_actual).strip()

        if normalized_actual == normalized_req:
            return actual

        common_words = set(normalized_req.split()) & set(normalized_actual.split())
        score = len(common_words)

        if score > best_score:
            best_score = score
            best_match = actual

    if best_score >= len(normalized_req.split()) * 0.6:
        return best_match

    return None


def _build_column_map(actual_cols: List[str]) -> Dict[str, str]:
    stripped_cols = [c.strip() for c in actual_cols]
    col_map: Dict[str, str] = {}

    for required in REQUIRED_COLUMNS:
        exact_index = -1
        for i, col in enumerate(stripped_cols):
            if col == required:
                exact_index = i
                break

        if exact_index >= 0:
            col_map[required] = actual_cols[exact_index]
            continue

        for actual in actual_cols:
            stripped_actual = actual.strip()
            if stripped_actual in KNOWN_TYPOS and KNOWN_TYPOS[stripped_actual] == required:
                col_map[required] = actual
                break
        else:
            match = _fuzzy_match(actual_cols, required)
            if match:
                col_map[required] = match

    return col_map


def load_excel(file_path: str) -> List[Dict[str, str]]:
    df: pd.DataFrame = pd.read_excel(file_path, dtype=str)
    df = df.fillna("")
    actual_cols: List[str] = df.columns.tolist()
    col_map: Dict[str, str] = _build_column_map(actual_cols)
    records: List[Dict[str, str]] = []
    for _, row in df.iterrows():
        row_dict: Dict[str, Any] = {}
        for required in REQUIRED_COLUMNS:
            if required in col_map:
                raw = row.get(col_map[required], "")
            else:
                raw = ""
            row_dict[required] = str(raw) if raw is not None else ""
        records.append(clean_row(row_dict))
    return records


def get_applicant(
    records: List[Dict[str, str]], serial_number: int
) -> Optional[Dict[str, str]]:
    if serial_number < 1 or serial_number > len(records):
        return None
    return records[serial_number - 1]


def get_total_applicants(records: List[Dict[str, str]]) -> int:
    return len(records)


def validate_excel_columns(file_path: str) -> bool:
    df: pd.DataFrame = pd.read_excel(file_path, nrows=0)
    actual_cols: List[str] = df.columns.tolist()
    col_map: Dict[str, str] = _build_column_map(actual_cols)
    for required in REQUIRED_COLUMNS:
        if required not in col_map:
            return False
    return True
