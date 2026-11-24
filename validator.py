"""Row validation: airport list loading, single-row checks, record building."""

from datetime import datetime
import math
import re


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    codes = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            code = line.strip()
            if not code or code.startswith("#"):
                continue
            codes.add(code)
    return codes


def _valid_dt(val: str) -> bool:
    if len(val) != 16 or val[10] != " ":
        return False
    try:
        datetime.strptime(val, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    vals = [x.strip() for x in fields]
    fid, orig, dest, dep, arr, prc = vals

    if any(v == "" for v in vals):
        return "MISSING_FIELD"

    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", fid):
        return "INVALID_FLIGHT_ID"

    if not re.fullmatch(r"[A-Z]{3}", orig) or orig not in airports:
        return "INVALID_ORIGIN"

    if not re.fullmatch(r"[A-Z]{3}", dest) or dest not in airports:
        return "INVALID_DESTINATION"

    if orig == dest:
        return "SAME_ORIGIN_DESTINATION"

    if not _valid_dt(dep):
        return "INVALID_DEPARTURE"

    if not _valid_dt(arr):
        return "INVALID_ARRIVAL"

    dep_dt = datetime.strptime(dep, "%Y-%m-%d %H:%M")
    arr_dt = datetime.strptime(arr, "%Y-%m-%d %H:%M")
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_val = float(prc)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price_val):
        return "INVALID_PRICE"

    if price_val <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    vals = [x.strip() for x in fields]
    return {
        "flight_id": vals[0],
        "origin": vals[1],
        "destination": vals[2],
        "departure_datetime": vals[3],
        "arrival_datetime": vals[4],
        "price": float(vals[5]),
    }
