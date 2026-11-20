"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""

import argparse
from datetime import datetime
import json
import logging
import os
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "260ADB181"
FIRST_NAME = "ABDOURAHAMANE"
LAST_NAME = "BARRY"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS)
    parser.add_argument("-i", "--input", action="append", default=[])
    parser.add_argument("-d", "--dir", action="append", default=[])
    parser.add_argument("-j", "--json", dest="json_in", default=None)
    parser.add_argument("-a", "--airports", default=None)
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("-q", "--query", default=None)
    parser.add_argument("-r", "--response", default=None)
    return parser


def _collect_csv_files(
    inputs: list[str], dirs: list[str]
) -> tuple[list[str], str | None]:
    files = []
    for p in inputs:
        if not os.path.isfile(p):
            return [], f"file not found: {p}"
        files.append(p)
    for d in dirs:
        if not os.path.isdir(d):
            return [], f"directory not found: {d}"
        csv_in_dir = []
        for name in sorted(os.listdir(d)):
            if name.lower().endswith(".csv"):
                full = os.path.join(d, name)
                if os.path.isfile(full):
                    csv_in_dir.append(full)
        if not csv_in_dir:
            return [], f"no .csv files in directory: {d}"
        files.extend(csv_in_dir)
    return files, None


def _setup_logger(log_path: str) -> tuple[logging.Logger, logging.Handler]:
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, handler


def _fail_runtime(logger: logging.Logger, msg: str) -> int:
    logger.warning(msg)
    print(f"Error: {msg}", file=sys.stderr)
    return 1


def _resolve_output_path(raw_out: str | None, default_name: str) -> str:
    if raw_out is None:
        return os.path.join(os.getcwd(), default_name)
    if os.path.isdir(raw_out):
        return os.path.join(raw_out, default_name)
    return raw_out


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code != 0 else 0

    has_csv = bool(args.input or args.dir)
    has_json = args.json_in is not None

    if not has_csv and not has_json:
        return 2
    if has_csv and has_json:
        return 2
    if has_csv and not args.airports:
        return 2
    if has_json and args.output is not None:
        return 2

    if args.output is not None:
        out_path = _resolve_output_path(args.output, "db.json")
        log_dir = os.path.dirname(os.path.abspath(out_path))
    else:
        out_path = os.path.join(os.getcwd(), "db.json")
        log_dir = os.getcwd()

    if args.response is not None and os.path.isdir(args.response):
        resp_abs = os.path.abspath(args.response)
        if os.path.abspath(log_dir) == resp_abs:
            log_dir = os.path.dirname(resp_abs) or resp_abs

    log_path = os.path.join(log_dir, "errors.log")
    logger, handler = _setup_logger(log_path)

    try:
        if has_json:
            try:
                with open(args.json_in, "r", encoding="utf-8") as f:
                    db = json.load(f)
            except OSError as exc:
                return _fail_runtime(logger, f"FILE_NOT_FOUND | {exc}")
            except json.JSONDecodeError as exc:
                return _fail_runtime(logger, f"INVALID_JSON | {exc}")

            if not isinstance(db, list):
                return _fail_runtime(
                    logger, f"INVALID_JSON | {args.json_in} does not contain a list"
                )
        else:
            try:
                airports = load_airports(args.airports)
            except OSError as exc:
                return _fail_runtime(logger, f"FILE_NOT_FOUND | {exc}")

            csv_files, collect_err = _collect_csv_files(args.input, args.dir)
            if collect_err is not None:
                return _fail_runtime(logger, f"INPUT_ERROR | {collect_err}")

            try:
                db, errors = parse_files(csv_files, airports)
            except OSError as exc:
                return _fail_runtime(logger, f"FILE_NOT_FOUND | {exc}")

            for err in errors:
                logger.warning(err)

            try:
                out_parent = os.path.dirname(os.path.abspath(out_path))
                if out_parent and not os.path.isdir(out_parent):
                    return _fail_runtime(logger, f"MISSING_OUTPUT_DIR | {out_parent}")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
            except OSError as exc:
                return _fail_runtime(logger, f"WRITE_ERROR | {exc}")

        if args.query is not None:
            try:
                with open(args.query, "r", encoding="utf-8") as f:
                    q_data = json.load(f)
            except OSError as exc:
                return _fail_runtime(logger, f"FILE_NOT_FOUND | {exc}")
            except json.JSONDecodeError as exc:
                return _fail_runtime(logger, f"INVALID_QUERY_FILE | {exc}")

            results = run_queries(db, q_data)
            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            default_resp = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            )
            resp_path = _resolve_output_path(args.response, default_resp)

            try:
                resp_parent = os.path.dirname(os.path.abspath(resp_path))
                if resp_parent and not os.path.isdir(resp_parent):
                    return _fail_runtime(logger, f"MISSING_OUTPUT_DIR | {resp_parent}")
                with open(resp_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
            except OSError as exc:
                return _fail_runtime(logger, f"WRITE_ERROR | {exc}")

        return 0
    finally:
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    sys.exit(main())
