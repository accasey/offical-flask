"""Configuration file for pytest."""

import os
import sys
import tempfile
from typing import Any, Generator, Optional

from flask import Flask, Response
from flask.testing import FlaskClient, FlaskCliRunner
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from flaskr import create_app  # noqa
from flaskr.db import get_db, init_db  # noqa

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app() -> Generator:
    """summary.

    Yields:
        [Flask]: [The Flask App]
    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({"TESTING": True, "DATABASE": db_path})

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Returns the testing client.

    Args:
        app (Flask): The Flask application.

    Returns:
        FlaskClient: The test client.
    """
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """Returns the testing running that can call the Click commands.

    Args:
        app (Flask): The Flask application.

    Returns:
        FlaskCliRunner: The CliRunning for testing the app's CLI commands.
    """
    return app.test_cli_runner()


class AuthActions:
    """A class to test the authentication actions."""

    def __init__(self: Any, client: FlaskClient) -> None:
        """Initialisation for the class.

        Args:
            client (FlaskClient): he flask client.
        """
        self._client: FlaskClient = client

    def login(
        self: Any, username: Optional[str] = "test", password: Optional[str] = "test",
    ) -> Response:
        """Testing logging into the application.

        Args:
            username (Optional[str], optional): The username. Defaults to "test".
            password (Optional[str], optional): The password. Defaults to "test".

        Returns:
            Response: The application's response object.
        """
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self: Any) -> Response:
        """Testing logging out of the application..

        Returns:
            Response: The application's response object.
        """
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    """A fixture for testing the AuthActions class.

    Args:
        client (FlaskClient): The flaskr application.

    Returns:
        AuthActions: An object to test the actions on.
    """
    return AuthActions(client)
