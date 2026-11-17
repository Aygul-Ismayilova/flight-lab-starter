"""Running queries against the flight database."""

from validator import is_valid_datetime

RECORD_KEYS = ["flight_id", "origin", "destination",
               "departure_datetime", "arrival_datetime", "price"]


def is_valid_query(query):
    """True if the query only uses allowed keys with values of the right type."""
    if not isinstance(query, dict):
        return False

    for key, value in query.items():
        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                return False
        elif key in ("departure_datetime", "arrival_datetime"):
            if not is_valid_datetime(value):
                return False
        elif key in ("price", "min_price"):
            # type() instead of isinstance(), because True/False count as int.
            if type(value) not in (int, float):
                return False
        elif key == "sort_by":
            if value not in RECORD_KEYS:
                return False
        elif key == "order":
            if value not in ("asc", "desc"):
                return False
        elif key == "limit":
            if type(value) is not int or value < 0:
                return False
        else:
            return False  # unknown key

    if "order" in query and "sort_by" not in query:
        return False
    return True


def flight_matches(flight, query):
    """True if the flight passes every condition in the query."""
    for key in ("flight_id", "origin", "destination"):
        if key in query and flight[key] != query[key]:
            return False
    if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
        return False
    if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
        return False
    if "price" in query and flight["price"] > query["price"]:
        return False
    if "min_price" in query and flight["price"] < query["min_price"]:
        return False
    return True

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [flight for flight in db if flight_matches(flight, query)]

    if "sort_by" in query:
        key = query["sort_by"]
        descending = query.get("order") == "desc"
        # sorted() keeps equal items in their original order, also with reverse=True.
        matches = sorted(matches, key=lambda flight: flight[key], reverse=descending)

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, list):
        return [run_query(db, query) for query in queries]
    return [run_query(db, queries)]
