"""Row validation: airport list loading, single-row checks, record building."""



import math
import re
from datetime import datetime

# We use [A-Za-z0-9] and [A-Z] instead of isalnum() / isupper(), because those
# also accept non-ASCII letters like "Ā" or "é".
FLIGHT_ID_PATTERN = re.compile(r"[A-Za-z0-9]{2,8}")
AIRPORT_PATTERN = re.compile(r"[A-Z]{3}")
DATETIME_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")


def is_valid_datetime(text):
    """True if text is a real date and time written exactly as YYYY-MM-DD HH:MM."""
    if not isinstance(text, str):
        return False
    if not DATETIME_PATTERN.fullmatch(text):
        return False
    try:
        datetime.strptime(text, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports = set()
    with open(path, encoding="utf-8") as file:
        for line in file:
            code = line.strip()
            if code == "" or code.startswith("#"):
                continue
            airports.add(code)
    return airports

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    # 1. exactly 6 fields
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    values = [field.strip() for field in fields]

    # 2. no empty fields
    if "" in values:
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price = values

    # 3. flight id
    if not FLIGHT_ID_PATTERN.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    # 4.-6. airports
    if not AIRPORT_PATTERN.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not AIRPORT_PATTERN.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    # 7.-9. dates
    if not is_valid_datetime(departure):
        return "INVALID_DEPARTURE"
    if not is_valid_datetime(arrival):
        return "INVALID_ARRIVAL"
    # Both strings have the format YYYY-MM-DD HH:MM, so comparing them as
    # strings gives the same answer as comparing the dates.
    if arrival <= departure:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # 10.-11. price
    try:
        amount = float(price)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(amount):  # nan, inf
        return "INVALID_PRICE"
    if amount <= 0:
        return "NON_POSITIVE_PRICE"

    return None



def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    values = [field.strip() for field in fields]
    return {
        "flight_id": values[0],
        "origin": values[1],
        "destination": values[2],
        "departure_datetime": values[3],
        "arrival_datetime": values[4],
        "price": float(values[5]),
    }