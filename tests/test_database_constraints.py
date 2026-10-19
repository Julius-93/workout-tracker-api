"""Bypass ORM setters to prove constraints are enforced inside the database."""
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Exercise, Workout, WorkoutExercise


def test_database_rejects_invalid_category(app):
    with app.app_context():
        with pytest.raises(IntegrityError):
            db.session.execute(db.text(
                "INSERT INTO exercises (name, category) VALUES ('Cycling', 'magic')"
            ))
            db.session.commit()
        db.session.rollback()


def test_database_rejects_blank_workout_name(app):
    with app.app_context():
        with pytest.raises(IntegrityError):
            db.session.execute(db.text(
                "INSERT INTO workouts (name, workout_date) VALUES ('  ', '2026-10-19')"
            ))
            db.session.commit()
        db.session.rollback()


def test_database_rejects_invalid_measure_and_orphan_fk(app):
    with app.app_context():
        db.session.add_all([
            Workout(name="Morning Run", workout_date=date(2026, 10, 19)),
            Exercise(name="Running", category="cardio"),
        ])
        db.session.commit()
        workout_id = db.session.scalar(db.select(Workout.id))
        exercise_id = db.session.scalar(db.select(Exercise.id))
        invalid_rows = [
            {"workout_id": workout_id, "exercise_id": exercise_id, "sets": -2, "reps": 10},
            {"workout_id": workout_id, "exercise_id": exercise_id, "sets": 2},
            {"workout_id": workout_id, "exercise_id": exercise_id},
            {"workout_id": 9999, "exercise_id": exercise_id, "duration_seconds": 10},
        ]
        for values in invalid_rows:
            with pytest.raises(IntegrityError):
                db.session.execute(db.insert(WorkoutExercise).values(**values))
                db.session.commit()
            db.session.rollback()


def test_database_rejects_duplicate_link(app):
    with app.app_context():
        workout = Workout(name="Leg Day", workout_date=date(2026, 10, 19))
        exercise = Exercise(name="Squats", category="strength")
        db.session.add_all([workout, exercise])
        db.session.commit()
        db.session.add(WorkoutExercise(workout_id=workout.id, exercise_id=exercise.id,
                                       sets=2, reps=12))
        db.session.commit()
        with pytest.raises(IntegrityError):
            db.session.execute(db.insert(WorkoutExercise).values(
                workout_id=workout.id, exercise_id=exercise.id, sets=3, reps=8
            ))
            db.session.commit()
        db.session.rollback()
