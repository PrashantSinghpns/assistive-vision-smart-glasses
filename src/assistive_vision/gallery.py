"""Validate local biometric galleries before model inference."""
import json
import math
from pathlib import Path


def validate_embedding(vector):
    if not isinstance(vector, (list, tuple)) or len(vector) != 128:
        raise ValueError("expected 128 finite numeric embedding values")
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) for value in vector):
        raise ValueError("expected 128 finite numeric embedding values")


def validate_records(records, *, allow_empty=False):
    if not isinstance(records, list) or (not records and not allow_empty):
        raise ValueError("gallery records must be a nonempty list")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("gallery records must be objects")
        name = record.get("name")
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise ValueError("identity names must be nonempty trimmed strings")
        if name.casefold() == "unknown" or any(ord(char) < 32 for char in name):
            raise ValueError("identity name is reserved or contains control characters")
        validate_embedding(record.get("embedding"))
    return records


def load_gallery(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read gallery: {error}") from error
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("expected gallery schema_version 1")
    return validate_records(data.get("records"))
