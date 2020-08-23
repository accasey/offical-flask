"""The blog."""
from typing import Any, Dict, Optional

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug import Response
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)


def get_post(id: int, check_author: Optional[bool] = True) -> Dict[str, str]:
    """Retrieve a specific post from the database.

    Args:
        id (int): The post id.
        check_author (bool, optional): Whether or not to check the author. \
        Defaults to True.

    Returns:
        Dict[str, str]: The post row returned as a dict.
    """
    post: Dict[str, str] = get_db().execute(
        "SELECT p.id, p.title, p.body, p.created, p.author_id, u.username"
        " FROM post p, user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (id,),
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} does not exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/")
def index() -> str:
    """The main index page for the Flaskr application.

    Returns:
        str: The HTML for index.html.
    """
    db: Any = get_db()
    posts: Dict[str, str] = db.execute(
        "SELECT p.id, p.title, p.body, p.created, p.author_id, u.username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY p.created DESC"
    ).fetchall()

    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create() -> Any:
    """Handles the create.html page.

    This method on a POST action will add to the database, whereas
    on a GET action it will return the HTML for the page.

    Returns:
        Any: Either the url for the index or the html for the create page.
    """
    if request.method == "POST":
        title: str = request.form["title"]
        body: str = request.form["body"]
        error: Any = None

        if not title:
            error = "Title is a required field."

        if error is not None:
            flash(error)
        else:
            db: Any = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=["GET", "POST"])
def update(id: int) -> Any:
    """Handles the create.html page.

    This method on a POST action will update the database, whereas
    on a GET action it will return the HTML for the page.

    Args:
        id (int): The post id.

    Returns:
        Any: Either the url for the index or the html for the create page.
    """
    post: Dict[str, str] = get_post(id)

    if request.method == "POST":
        title: str = request.form["title"]
        body: str = request.form["body"]
        error: Any = None

        if not title:
            error = "Title is a required field."

        if error is not None:
            flash(error)
        else:
            db: Any = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?" "WHERE id = ?", (title, body, id)
            )
            db.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=["POST"])
def delete(id: int) -> Response:
    """Delete an existing post.

    Args:
        id (int): The post id to delete.

    Returns:
        Response: The blog index url.
    """
    db: Any = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()

    return redirect(url_for("blog.index"))
