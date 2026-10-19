"""Isolation: each test gets a fresh database and Flask test client."""
import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def workout_payload():
    return {"name": "Morning Workout", "workout_date": "2026-10-19", "notes": "Warm up first"}


@pytest.fixture
def exercise_payload():
    return {"name": "Push-ups", "category": "strength", "description": "Upper body"}


@pytest.fixture
def entities(client, workout_payload, exercise_payload):
    workout = client.post("/api/workouts", json=workout_payload).get_json()
    exercise = client.post("/api/exercises", json=exercise_payload).get_json()
    return workout, exercise
