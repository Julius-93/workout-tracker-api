"""Reusable exercise catalogue CRUD (no update endpoint is required)."""
from flask import Blueprint, jsonify

from ..extensions import db
from ..models import Exercise
from ..schemas import ExerciseCreateSchema, ExerciseSchema
from .helpers import read_json_object

exercises_bp = Blueprint("exercises", __name__, url_prefix="/api/exercises")


@exercises_bp.get("")
def list_exercises():
    exercises = db.session.execute(db.select(Exercise).order_by(Exercise.id)).scalars().all()
    return jsonify(ExerciseSchema(many=True).dump(exercises)), 200


@exercises_bp.post("")
def create_exercise():
    data = ExerciseCreateSchema().load(read_json_object())
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return jsonify(ExerciseSchema().dump(exercise)), 201


@exercises_bp.get("/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    return jsonify(ExerciseSchema().dump(exercise)), 200


@exercises_bp.delete("/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return "", 204
