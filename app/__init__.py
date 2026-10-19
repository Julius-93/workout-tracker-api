"""App factory permits production, development and isolated pytest instances."""
import sqlite3

from flask import Flask, jsonify
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config
from .extensions import db, migrate
from .errors import register_error_handlers


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, connection_record):
    # SQLite requires this per connection; other database engines ignore it.
    if isinstance(connection, sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.sort_keys = False
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models to register metadata before Flask-Migrate discovers tables.
    from . import models  # noqa: F401
    from .routes.workouts import workouts_bp
    from .routes.exercises import exercises_bp

    app.register_blueprint(workouts_bp)
    app.register_blueprint(exercises_bp)
    register_error_handlers(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app
