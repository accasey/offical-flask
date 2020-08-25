"""Testing authentication."""

from flask import Flask, g, Response, session
from flask.testing import FlaskClient
import pytest

from flaskr.db import get_db
from tests.conftest import AuthActions


def test_register(client: FlaskClient, app: Flask) -> None:
    """Test the regsiter endpoint.

    Args:
        client (FlaskClient): The flask client.
        app (Flask): The application.
    """
    assert client.get("/auth/register").status_code == 200
    # If this failed, most likely a 500 internal server error.

    response: Response = client.post(
        "/auth/register", data={"username": "a", "password": "a"}
    )
    assert "http://localhost/auth/login" == response.headers["Location"]

    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = ?", ("a",)).fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        ("test", "test", b"already registered"),
    ),
)
def test_register_validate_input(
    client: FlaskClient, username: str, password: str, message: str
) -> None:
    """Test that the register endpoint is functioning correctly.

    Args:
        client (FlaskClient): The flask client.
        username (str): The username for the test.
        password (str): The password for the test.
        message (str): The message to check.
    """
    response: Response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client: FlaskClient, auth: AuthActions) -> None:
    """Test the login functionality.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The class with the auth methods.
    """
    assert client.get("/auth/login").status_code == 200

    response: Response = auth.login()
    assert response.headers["Location"] == "http://localhost/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", b"Incorrect username"), ("test", "a", b"Incorrect password"),),
)
def test_login_validate_input(
    auth: AuthActions, username: str, password: str, message: str
) -> None:
    """Test that the login endpoint is functioning correctly.

    Args:
        auth (AuthActions): The class with the actions.
        username (str): The username to test.
        password (str): The password to test.
        message (str): The message to check.
    """
    response: Response = auth.login(username, password)
    assert message in response.data


def test_logout(client: FlaskClient, auth: AuthActions) -> None:
    """Test the logout action.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The class with the methods to test the actions.
    """
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
