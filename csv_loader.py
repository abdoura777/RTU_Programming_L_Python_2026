"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records = []
    errors = []
    seen_ids = set()

    for path in paths:
        fname = os.path.basename(path)
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for line_no, row in enumerate(reader, start=1):
                if not row:
                    continue

                if line_no == 1:
                    first_col = row[0].strip().lower()
                    if first_col in ("flight_id", "id"):
                        continue

                err = validate_row(row, airports)
                if err is not None:
                    errors.append(f"{fname}:{line_no}: {err} | invalid flight row")
                    continue

                rec = to_record(row)
                fid = rec["flight_id"]
                if fid in seen_ids:
                    errors.append(f"{fname}:{line_no}: DUPLICATE_FLIGHT | duplicate flight_id {fid}")
                    continue

                seen_ids.add(fid)
                records.append(rec)

    return records, errors