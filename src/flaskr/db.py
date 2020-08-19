"""Ensure that the database is available."""
import sqlite3
from typing import Any

import click
from flask import current_app, Flask, g
from flask.cli import with_appcontext


def get_db() -> Any:
    """Returns an instance of the database.

    Returns:
        Any: The sqllite database
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e: Any = None) -> None:
    """Close the database instance and remove it from the global variable.

    Args:
        e (Any): Defaults to None.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db() -> None:
    """Initalise the database by creating the tables."""
    db = get_db()

    with current_app.open_resource("schema.sql", "r") as f:
        # db.executescript(f.read().decode("utf8"))
        db.executescript(f.read())


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialised the database")


def init_app(app: Flask) -> None:
    """Register the close_db and init_db_command functions with \
    the application instance."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
