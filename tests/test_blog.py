"""Testing the blog."""

from sqlite3 import Connection
from typing import Any, Dict, List

from flask import Flask, Response
from flask.testing import FlaskClient
import pytest

from flaskr.db import get_db
from tests.conftest import AuthActions


def test_index(client: FlaskClient, auth: AuthActions) -> None:
    """Testing the index.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The object which will login.
    """
    r: Response = client.get("/")
    assert b"Log In" in r.data
    assert b"Register" in r.data

    auth.login()
    r1: Response = client.get("/")
    assert b"Log Out" in r1.data
    assert b"test title" in r1.data
    assert b"by test n 2018-01-01" in r1.data
    assert b"test\nbody" in r1.data
    assert b"href='/1/update'" in r1.data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete",))
def test_login_required(client: FlaskClient, path: str) -> None:
    """Test login required feature.

    Test that when restricted routes are called that the login route\
    is returned.

    Args:
        client (FlaskClient): The flask testing client.
        path (str): The route to check.
    """
    r: Response = client.post(path)
    assert r.headers["Location"] == "http://localhost/auth/login"


def test_author_required(app: Flask, client: FlaskClient, auth: AuthActions) -> None:
    """Test that the author can make changes.

    Args:
        app (Flask): The flaskr application.
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The object which will login.
    """
    # Change the author id on the post
    with app.app_context():
        db: Connection = get_db()
        db.execute("UPDATE post SET author_id = ? WHERE id = ?", (2, 1))
        db.commit()

    auth.login()
    # the current user cannot modify the other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # the current user does not see the edit link
    assert b"href='/1/update'" not in client.get("/").data


@pytest.mark.parametrize("path", ("/2/update", "/2/delete",))
def test_exists_required(client: FlaskClient, auth: AuthActions, path: str) -> None:
    """Tests an invalid route.

    Invoke invalid routes as the post id does not exist. The application \
    should then return a 404 response.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The object which will login.
        path (str): The route to check.
    """
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    """Test creating a blog post.

    First make sure that the GET returns a 200 code. This is the same as \
    simulating the user clicking the 'New' link.

    Second test a POST, and execute a database query to count the number \
    of posts.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The object which will login.
        app (Flask): The flaskr application.
    """
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db: Connection = get_db()
        count: int = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_update(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    """Test updating a post.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The object which will login.
        app (Flask): The flaskr application.
    """
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db: Connection = get_db()
        post: Dict[str, str] = db.execute(
            "SELECT * FROM post WHERE id = ?", (1,)
        ).fetchone()
        assert post["title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/2/update"))
def test_create_update_validate(
    client: FlaskClient, auth: AuthActions, path: str
) -> None:
    """Test title required validation.

    When updating a post, the title is required. Test that this \
    requirement/constraint is working.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The object which will login.
        path (str): The route to check.
    """
    auth.login()
    r: Response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in r.data


def test_delete(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    """Test deleting a post.

    This should return the user to the index, and remove the post from \
    the database.

    Args:
        client (FlaskClient): The flask testing client.
        auth (AuthActions): The object which will login.
        app (Flask): The flaskr application.
    """
    auth.login()
    r: Response = client.post("/1/delete")
    assert r.headers["Location"] == "http://localhost/"

    with app.app_context():
        db: Connection = get_db()
        post: List[Any] = db.execute("SELECT * FROM post WHERE id = ?", (1,)).fetchone()
        assert post is None
