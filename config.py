"""Application configuration stored independently of the Flask factory."""
import os


class Config:
    # By default the SQLite database lives under instance/workouts.db.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///workouts.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
