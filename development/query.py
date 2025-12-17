"""Standalone Interactive SQLite Query Utility."""

import sqlite3
import sys
from pathlib import Path

from rich import box  # type: ignore  # noqa: PGH003
from rich.console import Console  # type: ignore  # noqa: PGH003
from rich.panel import Panel  # type: ignore  # noqa: PGH003
from rich.prompt import Prompt  # type: ignore  # noqa: PGH003
from rich.table import Table  # type: ignore  # noqa: PGH003

console = Console()
DB_PATH = Path("taskorbit.db")


def list_tables(conn: sqlite3.Connection) -> None:
    """Display a summary table of all existing tables and their row counts.

    Queries `sqlite_master` to find user-defined tables, then performs a
    count query on each to populate a summary table. Tables starting with
    'sqlite_' are automatically excluded.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = cursor.fetchall()

    if not tables:
        console.print("[yellow]No tables found in database.[/yellow]")
        return

    summary_table = Table(title="Database Schema", box=box.SIMPLE, show_header=True)
    summary_table.add_column("Table Name", style="cyan bold")
    summary_table.add_column("Row Count", justify="right", style="green")

    def get_row_count(table_name: str) -> str:
        try:
            count_cur = conn.execute(f"SELECT COUNT(*) FROM {table_name}")  # noqa: S608
            count = count_cur.fetchone()[0]
            return str(count)

        except sqlite3.Error:
            return "Error"

    for (table_name,) in tables:
        row_count = get_row_count(table_name)
        summary_table.add_row(table_name, row_count)

    console.print(summary_table)
    console.print("")


def display_transposed(headers: list[str], rows: list[sqlite3.Row]) -> None:
    """Render rows in a Side-by-Side Transposed format.

    Constructs a matrix where the first column contains field names and
    subsequent columns represent individual records. This avoids text wrapping
    issues common with wide tables.

    Format:
    Field       | Record 1 | Record 2 | Record 3 ...
    ------------+----------+----------+-------------
    id          | 123      | 456      | 789
    name        | A        | B        | C
    """
    if len(rows) > 10:  # noqa: PLR2004
        console.print(
            f"[yellow]Warning: Displaying {len(rows)} columns. "
            "This might wrap weirdly.[/yellow]"
        )

    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("Field", style="cyan bold", no_wrap=True)

    for i in range(1, len(rows) + 1):
        table.add_column(f"Rec {i}", style="white", overflow="fold")

    for header in headers:
        row_values = []
        for record in rows:
            val = record[header]
            val_str = str(val) if val is not None else "[dim]<NULL>[/dim]"
            row_values.append(val_str)

        table.add_row(header, *row_values)

    console.print(table)
    console.print(f"[dim i](Found {len(rows)} rows)[/dim i]\n")


def execute_query(conn: sqlite3.Connection, sql: str) -> None:
    """Execute SQL safely and route output to the console.

    Distinguishes between data modification queries (INSERT/UPDATE/DELETE),
    which print a success message and commit the transaction, and selection
    queries, which render the transposed results table.
    """
    sql = sql.strip()
    if not sql:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        if cursor.description is None:
            conn.commit()
            console.print(
                f"[bold green]✅ Success.[/bold green] Rows affected: {cursor.rowcount}"
            )
            return

        rows = cursor.fetchall()
        if not rows:
            console.print("[yellow]∅ No results found.[/yellow]")
            return

        headers = [d[0] for d in cursor.description]
        display_transposed(headers, rows)

    except sqlite3.Error as e:
        console.print(f"[bold red]🔥 SQLite Error:[/bold red] {e}")


def interactive_mode() -> None:
    """Run the Read-Eval-Print Loop (REPL).

    Establishes a persistent database connection and enters a loop accepting
    user input until an exit command ('q', 'quit', 'exit') or EOF is received.
    Also displays the schema summary on startup.
    """
    if not DB_PATH.exists():
        console.print(f"[bold red]❌ Error:[/bold red] Database not found at {DB_PATH}")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row

            welcome_msg = (
                "[bold green]TaskOrbit SQL Shell[/bold green]\n"
                f"[dim]Connected to: {DB_PATH}[/dim]\n"
                "Type [bold cyan]'q'[/bold cyan] to quit."
            )
            console.print(Panel(welcome_msg, box=box.ROUNDED, expand=False))
            list_tables(conn)

            while True:
                try:
                    query = Prompt.ask("[bold green]SQL[/bold green]")

                    if query.lower() in ("q", "quit", "exit"):
                        console.print("[bold green]Bye! 👋[/bold green]")
                        break

                    if not query:
                        continue

                    execute_query(conn, query)

                except KeyboardInterrupt:
                    console.print(
                        "\n[bold yellow]Interrupted. Type 'q' to quit.[/bold yellow]"
                    )
                    continue
                except EOFError:
                    break
    except sqlite3.Error as e:
        console.print(f"[bold red]Critical Error:[/bold red] {e}")


def main() -> None:
    """Entry point determining execution mode based on arguments.

    If command line arguments are present, they are treated as a single SQL
    query to execute immediately. Otherwise, the interactive shell is started.
    """
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        if DB_PATH.exists():
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                execute_query(conn, query)
        else:
            console.print(
                f"[bold red]❌ Error:[/bold red] Database not found at {DB_PATH}"
            )
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
