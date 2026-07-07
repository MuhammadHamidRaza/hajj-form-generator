from typing import Any, Dict, Optional
import math


def safe_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return ""
    if str(value).strip().lower() in ("none", "nan", "null", "nat"):
        return ""
    return str(value).strip()


def clean_row(row: Dict[str, Any]) -> Dict[str, str]:
    cleaned: Dict[str, str] = {}
    for key, value in row.items():
        cleaned[key] = safe_value(value)
    return cleaned


def is_empty(value: Optional[str]) -> bool:
    return value is None or value.strip() == ""


def format_date(value: str) -> str:
    if is_empty(value):
        return ""
    return value
