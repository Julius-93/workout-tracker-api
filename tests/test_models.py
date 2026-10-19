"""Direct ORM validation checks independently of Marshmallow."""
import pytest

from app.models import Exercise, Workout, WorkoutExercise


def test_workout_model_trims_name():
    workout = Workout(name="  Leg Day  ")
    assert workout.name == "Leg Day"


@pytest.mark.parametrize("invalid", ["  ", "ab", "x" * 101, None])
def test_workout_model_rejects_bad_name(invalid):
    with pytest.raises(ValueError):
        Workout(name=invalid)


def test_exercise_model_rejects_unknown_category():
    with pytest.raises(ValueError):
        Exercise(name="Bench press", category="underwater")


def test_model_rejects_long_description():
    with pytest.raises(ValueError):
        Exercise(name="Running", category="cardio", description="X" * 501)


def test_model_rejects_nonpositive_measure():
    with pytest.raises(ValueError):
        WorkoutExercise(sets=0)


def test_model_rejects_boolean_measure():
    with pytest.raises(ValueError):
        WorkoutExercise(reps=True)
