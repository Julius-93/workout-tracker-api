"""Workout resource endpoints and workout-to-exercise association endpoint."""
from flask import Blueprint, jsonify

from ..extensions import db
from ..models import Exercise, Workout, WorkoutExercise
from ..schemas import (
    WorkoutCreateSchema,
    WorkoutExerciseCreateSchema,
    WorkoutExerciseSchema,
    WorkoutSchema,
)
from .helpers import read_json_object

workouts_bp = Blueprint("workouts", __name__, url_prefix="/api/workouts")


@workouts_bp.get("")
def list_workouts():
    workouts = db.session.execute(db.select(Workout).order_by(Workout.id)).scalars().all()
    return jsonify(WorkoutSchema(many=True).dump(workouts)), 200


@workouts_bp.post("")
def create_workout():
    data = WorkoutCreateSchema().load(read_json_object())
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(WorkoutSchema().dump(workout)), 201


@workouts_bp.get("/<int:workout_id>")
def get_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    return jsonify(WorkoutSchema().dump(workout)), 200


@workouts_bp.delete("/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    db.session.delete(workout)
    db.session.commit()
    return "", 204


@workouts_bp.post("/<int:workout_id>/exercises")
def add_exercise_to_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    data = WorkoutExerciseCreateSchema().load(read_json_object())
    exercise = db.get_or_404(Exercise, data["exercise_id"])

    existing = db.session.execute(
        db.select(WorkoutExercise).filter_by(workout_id=workout.id, exercise_id=exercise.id)
    ).scalar_one_or_none()
    if existing is not None:
        return jsonify({"error": "This exercise is already in the workout."}), 409

    association = WorkoutExercise(workout=workout, exercise=exercise,
                                  sets=data.get("sets"), reps=data.get("reps"),
                                  duration_seconds=data.get("duration_seconds"))
    db.session.add(association)
    db.session.commit()
    return jsonify(WorkoutExerciseSchema().dump(association)), 201
