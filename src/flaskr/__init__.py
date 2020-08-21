"""Use an application factory to create the Flask instance."""
import os
from typing import Dict

from flask import Flask

__version__ = "0.1.0"


def create_app(test_config: Dict[str, str] = None) -> Flask:
    """Create and configure the app object."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "flaskr.sqlite")
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # A simple page that says hello
    @app.route("/hello")
    def hello() -> str:
        return "<h1>Hello, World!</h1>"

    from . import db

    db.init_app(app)

    from . import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    return app
