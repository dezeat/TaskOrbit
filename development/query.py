"""Standalone SQLite Query Utility.

Allows querying the app database without initializing the Flask application context,
bypassing circular import issues.
"""

import argparse
import sqlite3
import sys
from pathlib import Path

from app.utils.logger import logger

SEARCH_PATHS = [".", "instance", "app"]
EXTENSIONS = {".db", ".sqlite", ".sqlite3"}


def find_database() -> Path:
    """Locates the first valid SQLite database file in standard Flask directories.

    Returns:
        Path: The path to the found database file.

    Raises:
        FileNotFoundError: If no database file is found in SEARCH_PATHS.
    """
    root = Path.cwd()

    for search_dir in SEARCH_PATHS:
        path = root / search_dir
        if not path.exists():
            continue

        for file in path.iterdir():
            if file.suffix in EXTENSIONS:
                return file
    msg = (
        f"Could not find a database file in {SEARCH_PATHS} with extensions {EXTENSIONS}"
    )
    raise FileNotFoundError(msg)


def format_row(row: sqlite3.Row) -> str:
    """Formats a single database row for display."""
    return " | ".join(f"{item!s:<15}" for item in row)


def execute_query(db_path: Path, sql: str, params: tuple = ()) -> None:
    """Executes a raw SQL query against the specified database and logs the results.

    Args:
        db_path (Path): Path to the SQLite database.
        sql (str): The SQL query string.
        params (tuple): Parameters for the SQL query.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            if not rows:
                msg = f"Query executed successfully. Rows affected: {cursor.rowcount}"
                logger.info(msg)
                return

            headers = list(rows[0].keys())
            header_str = " | ".join(f"{h:<15}" for h in headers)
            separator = "-" * len(header_str)

            logger.info(header_str)
            logger.info(separator)

            for row in rows:
                logger.info(format_row(row))

    except sqlite3.Error as e:
        msg = f"SQLite Error: {e}"
        logger.exception(msg)


def main() -> None:
    """Main execution entry point parsing command line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute raw SQL against the SQLite database."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="SQL query to execute. If omitted, enters interactive mode.",
    )
    parser.add_argument("--db", type=Path, help="Explicit path to the database file.")

    args = parser.parse_args()

    try:
        db_path = args.db if args.db else find_database()
        msg = f"Using database at: {db_path.resolve()}"
        logger.info(msg)

    except FileNotFoundError as e:
        msg = f"Database file not found: {e}"
        logger.critical(msg)
        sys.exit(1)

    if args.query:
        execute_query(db_path, args.query)

    else:
        execute_query(db_path, "SELECT name FROM sqlite_master WHERE type='table'")
        logger.info("\nInteractive Mode (Type 'q' to exit)")

        while True:
            try:
                query = input("\nSQL> ").strip()

                if query.lower() in ("q", "quit", "exit"):
                    break

                if not query:
                    continue
                execute_query(db_path, query)

            except KeyboardInterrupt:
                logger.info("\nExiting...")
                break


if __name__ == "__main__":
    main()
