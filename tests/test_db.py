"""Test the database."""

import sqlite3
from sqlite3 import Connection
from typing import Any

from flask import Flask
from flask.testing import FlaskCliRunner
import pytest

from flaskr.db import get_db


def test_get_close_db(app: Flask) -> None:
    """Test that the database is closed.

    Args:
        app (Flask): The Flask application.
    """
    with app.app_context():
        db: Connection = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")
    assert "closed" in str(e.value)


def test_init_db_command(runner: FlaskCliRunner, monkeypatch: Any) -> None:
    """Replaces the init_db function.

    Uses Pytest's monkeypatch fixture to replace the init_db function\
    with one that records that it has been called.

    Args:
        runner (FlaskCliRunner): The runner used to invoke click.
        monkeypatch (Any): The monkeypatch fixture.
    """

    class Recorder(object):
        called: bool = False

    def fake_init_db() -> None:
        Recorder.called = True

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
