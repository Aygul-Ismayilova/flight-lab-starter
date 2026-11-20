# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->


## Tools used

- Gemini (2026)

## Conversation links

- Link 1: https://share.gemini.google/ToXpMXAHYvVd
- Link 2:

## What I used them for

- Understanding validation rules, date checks, argparse, JSON handling, and code structure.
- Generating/simplifying starter code and explaining how parts of the program work.

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| validator.py | is_valid_datetime, load_airports, validate_row, to_record | Explained and modified (I removed extra helpers/constants) |
| csv_loader.py | parse_files | AI generated and I reviewed |
| query.py | run_query, run_queries | AI generated and I reviewed |
| flight_parser.py | main, CLI and logging setup/cleanup | AI generated and I reviewed |

## Key prompts

1. How do I check that a string is YYYY-MM-DD HH:MM and is a real date?
2. How do I use argparse so that one of -i, -d, -j is required?
3. Write simple Python code for the flight parser modules using only the standard library.

## What I changed or verified myself

- Simplified validator.py and ran tests to verify validation checks, log cleanup, and query outputs.
