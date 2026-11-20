"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import argparse
import json
import logging
import os

from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports


# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB153"
FIRST_NAME = "Aygul"
LAST_NAME = "Ismayilova"

def load_json(path):
    with open(path, encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"{path} is not valid JSON")


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def is_list_of_dicts(data):
    return isinstance(data, list) and all(isinstance(item, dict) for item in data)


def csv_files_in_folder(folder):
    """Paths of the .csv files directly inside folder, in sorted name order."""
    paths = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if name.endswith(".csv") and os.path.isfile(path):
            paths.append(path)
    if not paths:
        raise ValueError(f"no .csv files found in {folder}")
    return paths


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = argparse.ArgumentParser(description="Flight schedule parser and query tool")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="parse one CSV file")
    source.add_argument("-d", metavar="FOLDER", help="parse every .csv file in a folder")
    source.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list (needed with -i and -d)")
    parser.add_argument("-o", metavar="FILE", help="database output path (default: db.json)")
    parser.add_argument("-q", metavar="FILE", help="JSON file with queries")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="folder for the response file")

    # On a usage error argparse prints a message and exits with code 2.
    args = parser.parse_args(argv)
    if (args.i or args.d) and not args.a:
        parser.error("-a is required with -i and -d")
    if args.j and args.o:
        parser.error("-o cannot be used with -j")
    db_path = args.o or "db.json"

    logger = logging.getLogger("flight_parser")
    handler = None
    try:
        if args.j:
            db = load_json(args.j)
            if not is_list_of_dicts(db):
                raise ValueError(f"{args.j} must contain a JSON array of objects")
        else:
            # errors.log goes into the same folder as the database file.
            log_path = os.path.join(os.path.dirname(db_path), "errors.log")
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(handler)

            if args.i:
                paths = [args.i]
            else:
                paths = csv_files_in_folder(args.d)
            airports = load_airports(args.a)

            db, errors = parse_files(paths, airports)
            for message in errors:
                logger.warning(message)
            save_json(db_path, db)
            print(f"{len(db)} valid rows, {len(errors)} invalid rows")

        if args.q:
            queries = load_json(args.q)
            if not (isinstance(queries, dict) or is_list_of_dicts(queries)):
                raise ValueError(f"{args.q} must contain a query object or an array of them")
            responses = run_queries(db, queries)
            time_stamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{time_stamp}.json"
            save_json(os.path.join(args.r, file_name), responses)
            print(f"Response written to {file_name}")

    # OSError: a file or folder is missing or cannot be read/written.
    # ValueError: bad JSON, wrong JSON shape, no .csv files, not UTF-8 text.
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        # Always remove the handler, so the next main() call starts clean.
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
