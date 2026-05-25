"""
ETL — Extract stage

Reads a CSV or Excel file into a pandas DataFrame. The caller is
responsible for passing the file kind (so the same code can be reused
both for uploaded files in memory and for local file paths).

Supported inputs:
    * CSV   (`.csv`)  — read with pandas.read_csv
    * Excel (`.xls`, `.xlsx`) — read with pandas.read_excel (engine=openpyxl)

Returns a DataFrame with the raw, untouched columns. All cleaning
happens downstream in `transform.py`.
"""

import io
from typing import IO, Tuple

import pandas as pd

SUPPORTED_KINDS = {"csv", "xlsx", "xls"}


def detect_kind(filename: str) -> str:
    """Infer the source kind from a filename's extension."""
    lower = (filename or "").lower()
    if lower.endswith(".csv"):
        return "csv"
    if lower.endswith(".xlsx"):
        return "xlsx"
    if lower.endswith(".xls"):
        return "xls"
    raise ValueError(
        f"Unsupported file kind for '{filename}'. Expected one of: {SUPPORTED_KINDS}"
    )


def extract_from_path(path: str) -> Tuple[pd.DataFrame, str]:
    """Read a file from disk and return (DataFrame, kind)."""
    kind = detect_kind(path)
    if kind == "csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path, engine="openpyxl")
    return df, kind


def extract_from_bytes(
    contents: bytes, filename: str
) -> Tuple[pd.DataFrame, str]:
    """Read a file from an in-memory bytes buffer (e.g. upload)."""
    kind = detect_kind(filename)
    buf = io.BytesIO(contents)
    if kind == "csv":
        df = pd.read_csv(buf)
    else:
        df = pd.read_excel(buf, engine="openpyxl")
    return df, kind


def extract_from_stream(
    stream: IO[bytes], filename: str
) -> Tuple[pd.DataFrame, str]:
    """Read a file from a binary stream."""
    return extract_from_bytes(stream.read(), filename)
