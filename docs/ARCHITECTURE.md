# Design decisions and request lifecycle

## Entities

- `Workout`: workout title, workout date, optional notes.
- `Exercise`: reusable definition with name, category and description.
- `WorkoutExercise`: **association object** storing the workout ID, exercise ID and contextual sets/reps/duration. This is not a plain two-column many-to-many table because the link contains user-facing data.

`Workout -> WorkoutExercise` is one-to-many. `Exercise -> WorkoutExercise` is also one-to-many. Together they implement many-to-many reuse.

## Request flow

```text
POST /api/workouts/1/exercises
  -> read_json_object (content type / valid JSON object)
  -> WorkoutExerciseCreateSchema.load (Marshmallow field + cross-field checks)
  -> db.get_or_404 (resolve linked rows)
  -> duplicate association check (HTTP 409)
  -> WorkoutExercise model setters (@validates)
  -> db.session.commit (named constraints, FK, uniqueness)
  -> WorkoutExerciseSchema.dump (nested Exercise details)
  -> HTTP 201 JSON
```

## Three distinct protection layers

1. **Schema validators** safeguard incoming request types, lengths, categorical values and valid combinations of measurement fields. Bad requests receive HTTP 400 before ORM insertion.
2. **Model validators** run on Python/SQLAlchemy assignments, including those created outside HTTP routes. They strip names and reject blank titles, illegal categories, or nonpositive measurements.
3. **Database constraints** are independent of the schema and ORM validation. Named `CHECK` constraints and `UNIQUE` prevent invalid rows inserted through direct SQL; FK checks enforce referential integrity.

## RESTful constraints

- `GET`: 200
- `POST`: 201
- `DELETE`: 204
- `404`: referenced resource doesn't exist
- `409`: association duplicate or DB-level integrity conflict
- No PUT/PATCH actions per task specification.

## Migrations

Migrations are generated with `flask db init`, `flask db migrate` and `flask db upgrade`, then reviewed and committed. No `db.create_all()` in production app startup: migrations are the source of truth. The test fixture alone calls `db.create_all()` for test isolation.

## Not included

No authentication, JWT, user registration, frontend, exercise editing, individual association deletion or production deployment settings. These are outside the shared rubric scope.
