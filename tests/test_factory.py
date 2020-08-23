"""Test factory for the application."""

from flask import Response
from flask.testing import FlaskClient

from flaskr import create_app


def test_config() -> None:
    """Test the configuration."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_hello(client: FlaskClient) -> None:
    """Test the hello route.

    Args:
        client (FlaskClient): The flaskr test client.
    """
    response: Response = client.get("/hello")
    assert response.data == b"Hello, World!"
