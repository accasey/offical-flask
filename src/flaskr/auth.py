"""Authentication for the Flaskr application."""

import functools
from sqlite3 import Connection
from typing import Any, Dict

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug import Response
from werkzeug.security import check_password_hash, generate_password_hash


from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register() -> Any:
    """Handle the registration form.

    Returns:
        Any: Either The HTML for the form (GET) or a URL (POST).
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db: Connection = get_db()
        error: Any = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif (
            db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            is not None
        ):
            error = f"User {username} is already registered."

        if error is None:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login() -> Any:
    """Handle the login form.

    Either validating credentials or presenting the form for login.

    Returns:
        Any: Either The HTML for the form (GET) or a URL (POST).
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db: Connection = get_db()
        error: Any = None

        user: Dict[str, str] = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user() -> None:
    """Checks if a user id is stored in the session.

    Gets that user’sdata from the database, storing it in g.user, which lasts\
    for the length of the request.

    If there is no user id, or if the id doesn’t exist, g.user will be None.
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/logout")
def logout() -> Response:
    """Logs out the current user and returns the index page.

    Returns:
        Response: The url for the index page.
    """
    session.clear()
    return redirect(url_for("index"))


def login_required(view: Any) -> Any:
    """This decorator returns a new view function that wraps the original view.

    The new function checks if a user is loaded and redirects to the login pagez
    otherwise.\
    If a user is loaded the original view is called and continues normally.\
    This decorator will be used with the blog views.

    Args:
        view (Any): The view function to be decorated.

    Returns:
        Any: The decorated view function.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs: Any) -> Any:
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
