"""Marshmallow request validation and nested JSON response serialization."""
from marshmallow import Schema, ValidationError, fields, validate, validates_schema


# The schema stops malformed requests before they reach the model or database.
name_validators = [
    validate.Length(min=3, max=100),
    validate.Regexp(r".*\S.*", error="Name must not be blank."),
]


class WorkoutCreateSchema(Schema):
    name = fields.Str(required=True, validate=name_validators)
    workout_date = fields.Date(required=True)
    notes = fields.Str(allow_none=True, validate=validate.Length(max=500))


class ExerciseCreateSchema(Schema):
    name = fields.Str(required=True, validate=name_validators)
    category = fields.Str(
        required=True,
        validate=validate.OneOf(["strength", "cardio", "mobility"]),
    )
    description = fields.Str(allow_none=True, validate=validate.Length(max=500))


class WorkoutExerciseCreateSchema(Schema):
    exercise_id = fields.Int(required=True, validate=validate.Range(min=1), strict=True)
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1), strict=True)
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1), strict=True)
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1), strict=True)

    @validates_schema
    def validate_training_measure(self, data, **kwargs):
        """Require either complete sets/reps, a duration, or both."""
        has_sets = data.get("sets") is not None
        has_reps = data.get("reps") is not None
        has_duration = data.get("duration_seconds") is not None

        if has_sets != has_reps:
            raise ValidationError("Sets and reps must be provided together.")
        if not (has_sets and has_reps) and not has_duration:
            raise ValidationError("Provide sets and reps, or duration_seconds.")


class ExerciseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    category = fields.Str()
    description = fields.Str(allow_none=True)


class WorkoutExerciseSchema(Schema):
    id = fields.Int()
    workout_id = fields.Int()
    exercise_id = fields.Int()
    sets = fields.Int(allow_none=True)
    reps = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)
    exercise = fields.Nested(ExerciseSchema)


class WorkoutSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    workout_date = fields.Date()
    notes = fields.Str(allow_none=True)
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema))
