"""Exercise request validation even without a running Flask server."""
import pytest
from marshmallow import ValidationError

from app.schemas import ExerciseCreateSchema, WorkoutCreateSchema, WorkoutExerciseCreateSchema


def test_marshmallow_parses_iso_date():
    parsed = WorkoutCreateSchema().load({"name": "Leg Day", "workout_date": "2026-10-19"})
    assert parsed["workout_date"].isoformat() == "2026-10-19"


def test_marshmallow_blocks_unknown_category():
    with pytest.raises(ValidationError):
        ExerciseCreateSchema().load({"name": "Walking", "category": "unknown"})


def test_marshmallow_blocks_incomplete_sets_reps():
    with pytest.raises(ValidationError):
        WorkoutExerciseCreateSchema().load({"exercise_id": 1, "sets": 3})


def test_marshmallow_blocks_unknown_field():
    with pytest.raises(ValidationError):
        WorkoutCreateSchema().load({"name": "Leg Day", "workout_date": "2026-10-19",
                                    "is_admin": True})
