"""Relational entities and ORM-level validations for a training application."""
from sqlalchemy.orm import validates

from .extensions import db


class Workout(db.Model):
    """A dated workout that may contain several reusable exercises."""

    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    workout_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.String(500), nullable=True)

    __table_args__ = (
        db.CheckConstraint("length(trim(name)) >= 3", name="ck_workouts_name_min_length"),
    )

    # Deleting a workout removes its join records but not its reusable exercises.
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or not 3 <= len(value.strip()) <= 100:
            raise ValueError("Workout name must contain 3 to 100 characters.")
        return value.strip()

    @validates("notes")
    def validate_notes(self, key, value):
        if value is not None and (not isinstance(value, str) or len(value) > 500):
            raise ValueError("Workout notes cannot exceed 500 characters.")
        return value


class Exercise(db.Model):
    """An exercise definition that can be added to more than one workout."""

    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(500), nullable=True)

    __table_args__ = (
        db.CheckConstraint("length(trim(name)) >= 3", name="ck_exercises_name_min_length"),
        db.CheckConstraint(
            "category IN ('strength', 'cardio', 'mobility')",
            name="ck_exercises_category_allowed",
        ),
    )

    # Deleting an exercise removes its join records but not the workouts.
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or not 3 <= len(value.strip()) <= 100:
            raise ValueError("Exercise name must contain 3 to 100 characters.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if value not in {"strength", "cardio", "mobility"}:
            raise ValueError("Category must be strength, cardio, or mobility.")
        return value

    @validates("description")
    def validate_description(self, key, value):
        if value is not None and (not isinstance(value, str) or len(value) > 500):
            raise ValueError("Exercise description cannot exceed 500 characters.")
        return value


class WorkoutExercise(db.Model):
    """Association object; stores exercise-specific details within one workout."""

    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
        db.CheckConstraint("sets IS NULL OR sets > 0", name="ck_link_positive_sets"),
        db.CheckConstraint("reps IS NULL OR reps > 0", name="ck_link_positive_reps"),
        db.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_link_positive_duration",
        ),
        db.CheckConstraint(
            "(sets IS NULL AND reps IS NULL) OR (sets IS NOT NULL AND reps IS NOT NULL)",
            name="ck_link_sets_and_reps_together",
        ),
        db.CheckConstraint(
            "(sets IS NOT NULL AND reps IS NOT NULL) OR duration_seconds IS NOT NULL",
            name="ck_link_has_training_measure",
        ),
    )

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("sets", "reps", "duration_seconds")
    def validate_positive_measure(self, key, value):
        if value is not None and (type(value) is not int or value <= 0):
            raise ValueError(f"{key} must be a positive integer when provided.")
        return value
