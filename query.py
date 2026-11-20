"""Running queries against the flight database."""

from datetime import datetime


def _parse_dt_filter(val: str) -> datetime | None:
    if not isinstance(val, str):
        return None
    val = val.strip()
    if len(val) == 10:
        try:
            return datetime.strptime(val, "%Y-%m-%d")
        except ValueError:
            return None
    if len(val) == 16 and val[10] == " ":
        try:
            return datetime.strptime(val, "%Y-%m-%d %H:%M")
        except ValueError:
            return None
    return None


def _valid_full_dt(val: str) -> bool:
    if not isinstance(val, str):
        return False
    s = val.strip()
    if len(s) != 16 or s[10] != " ":
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def _is_number(val) -> bool:
    return not isinstance(val, bool) and isinstance(val, (int, float))


def _matches_dt_bound(rec_str: str, filter_val: str, mode: str) -> bool:
    dt = _parse_dt_filter(filter_val)
    if dt is None:
        return False
    rec_dt = datetime.strptime(rec_str, "%Y-%m-%d %H:%M")
    if mode == "after":
        return rec_dt >= dt
    return rec_dt <= dt


def _matches_query(rec: dict, q: dict) -> bool:
    for key, val in q.items():
        if val is None or key in ("sort_by", "order", "limit"):
            continue
        if key == "flight_id" and rec.get("flight_id") != val:
            return False
        elif key == "origin" and rec.get("origin") != val:
            return False
        elif key == "destination" and rec.get("destination") != val:
            return False
        elif key == "price" and rec.get("price", 0) > val:
            return False
        elif key == "max_price" and rec.get("price", 0) > val:
            return False
        elif key == "min_price" and rec.get("price", 0) < val:
            return False
        elif key == "departure_after" and not _matches_dt_bound(rec["departure_datetime"], val, "after"):
            return False
        elif key == "departure_before" and not _matches_dt_bound(rec["departure_datetime"], val, "before"):
            return False
        elif key == "departure_datetime" and not _matches_dt_bound(rec["departure_datetime"], val, "after"):
            return False
        elif key == "arrival_datetime" and not _matches_dt_bound(rec["arrival_datetime"], val, "before"):
            return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not isinstance(query, dict):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    allowed_keys = {
        "flight_id",
        "origin",
        "destination",
        "price",
        "max_price",
        "min_price",
        "departure_after",
        "departure_before",
        "departure_datetime",
        "arrival_datetime",
        "sort_by",
        "order",
        "limit",
    }
    if not set(query.keys()).issubset(allowed_keys):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for str_key in ("flight_id", "origin", "destination"):
        if str_key in query and query[str_key] is not None and not isinstance(query[str_key], str):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for num_key in ("price", "max_price", "min_price"):
        if num_key in query and query[num_key] is not None:
            if not _is_number(query[num_key]) or query[num_key] < 0:
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for dt_key in ("departure_after", "departure_before"):
        if dt_key in query and query[dt_key] is not None:
            if _parse_dt_filter(query[dt_key]) is None:
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for exact_dt_key in ("departure_datetime", "arrival_datetime"):
        if exact_dt_key in query and query[exact_dt_key] is not None:
            if not _valid_full_dt(query[exact_dt_key]):
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

    sort_fields = {
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price",
    }
    sort_by = query.get("sort_by")
    if sort_by is not None and sort_by not in sort_fields:
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    order = query.get("order")
    if order is not None and order not in ("asc", "desc"):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if order is not None and sort_by is None:
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    limit = query.get("limit")
    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [dict(rec) for rec in db if _matches_query(rec, query)]

    if sort_by is not None:
        reverse = order == "desc"
        matches.sort(key=lambda r: r.get(sort_by), reverse=reverse) # pyright: ignore[reportArgumentType]

    if limit is not None:
        matches = matches[:limit]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        return [run_query(db, queries)]
    if isinstance(queries, list):
        return [run_query(db, q) for q in queries]
    return [run_query(db, queries)]