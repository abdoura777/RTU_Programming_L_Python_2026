"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given."""
    records: list[dict] = []
    errors: list[str] = []
    seen_flights: set[tuple[str, str]] = set()

    for path in paths:
        fname = os.path.basename(path)
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for line_no, row in enumerate(reader, start=1):
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                first = row[0].strip()
                if first.startswith("#"):
                    continue

                if line_no == 1 and first.lower() in ("flight_id", "id"):
                    continue

                err = validate_row(row, airports)
                if err is not None:
                    errors.append(f"{fname}:{line_no}: {err} | invalid row")
                    continue

                rec = to_record(row)
                dep_date = rec["departure_datetime"][:10]
                key = (rec["flight_id"], dep_date)
                if key in seen_flights:
                    errors.append(
                        f"{fname}:{line_no}: DUPLICATE_FLIGHT | duplicate flight {rec['flight_id']} on {dep_date}"
                    )
                    continue

                seen_flights.add(key)
                records.append(rec)

    return records, errors
