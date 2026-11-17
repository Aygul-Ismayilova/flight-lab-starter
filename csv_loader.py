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
    seen = set()  # (flight_id, departure_datetime) of every valid flight so far

    for path in paths:
        file_name = os.path.basename(path)
        # Text mode turns both "\n" and "\r\n" line endings into "\n".
        with open(path, encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.rstrip("\r\n")

                if line_number == 1:
                    continue  # header
                if line.strip() == "" or line.strip().startswith("#"):
                    continue  # blank line or comment

                fields = next(csv.reader([line]))
                error = validate_row(fields, airports)

                if error is None:
                    record = to_record(fields)
                    key = (record["flight_id"], record["departure_datetime"])
                    if key in seen:
                        error = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(record)

                if error is not None:
                    errors.append(f"{file_name}:{line_number}: {error} | {line}")

    return records, errors

