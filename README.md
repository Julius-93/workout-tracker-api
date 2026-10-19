# Flask SQLAlchemy Workout Tracking API

A modular, RESTful Flask backend for personal trainers. A workout contains reusable exercises, and each workout-exercise link records sets/reps, duration, or both. Built for the **Summative Lab: Flask SQLAlchemy Workout Application Backend**.

## Features

- Create, list, retrieve, and delete **workouts** and **exercises**.
- Attach an existing exercise to any workout; reuse the same exercise across different workouts.
- Three models (`Workout`, `Exercise`, `WorkoutExercise`) with two one-to-many relationships representing many-to-many reuse.
- Marshmallow validation and nested serialization.
- Several ORM/model validations, database `CHECK` and `UNIQUE` constraints, foreign keys, and friendly API errors.
- Flask-Migrate migrations, idempotent development seed file, isolated pytest suite and GitHub Actions.
- Intentional scope: **no PUT/PATCH operations**, and no endpoint to remove an individual workout-exercise link.

## Tech stack

Python 3.11, Flask 2.2.2, Flask-SQLAlchemy 3.0.3, Flask-Migrate 3.1.0, Marshmallow 3.20.1, SQLAlchemy 2.0.36, Alembic 1.14.1, SQLite (development), Pipenv and pytest. Pinned Flask/Marshmallow versions follow the coursework's prescribed legacy versions; these are not necessarily suitable for a new production deployment without a security/dependency upgrade.

## Relational design

```text
Workout (1) --------< WorkoutExercise >-------- (1) Exercise
id PK                    id PK                       id PK
name                     workout_id FK               name
workout_date             exercise_id FK              category
notes                    sets                        description
                         reps
                         duration_seconds
                         UNIQUE(workout_id, exercise_id)
```

One workout has many association records. One exercise has many association records, enabling reuse in multiple workouts. A pair `(workout_id, exercise_id)` is unique by design (no duplicate entry for the same exercise within one workout). Removing either parent removes relevant association records while preserving the other parent.

## Installation (Ubuntu / WSL)

```bash
cd ~/Julius_Dev/workout-tracker-api
python --version  # 3.11.x recommended
python -m pip install --user pipenv  # only if not installed
pipenv --python 3.11
pipenv install --dev
```

If using pyenv and already have Python 3.11.9 installed:

```bash
pyenv local 3.11.9
pipenv --python "$(pyenv which python)"
pipenv install --dev
```

Pipenv may fail to create environments for older Python 3.8 installations with a modern virtualenv seeder. Use Python 3.11 for this lab unless your institution mandates an older runtime.

## Database migrations and seeding

Run from the project root:

```bash
pipenv run flask --app wsgi:app db init
pipenv run flask --app wsgi:app db migrate -m "Create workout, exercise and association tables"
pipenv run flask --app wsgi:app db upgrade
pipenv run python seed.py
```

**Important:** `db init` is only run once per repository; after migrations are checked into Git, collaborators use **only** `pipenv run flask --app wsgi:app db upgrade`. Review and commit the generated `migrations/` folder to Git (not the SQLite database). `seed.py` **resets all workout/exercise data**, and is intended for development and demonstration only.

Database by default: `instance/workouts.db`. The folder is gitignored. Override via `DATABASE_URL` as needed.

## Run the API

```bash
pipenv run flask --app wsgi:app run --debug
```

Default base URL: `http://127.0.0.1:5000`. Check health:

```bash
curl -i http://127.0.0.1:5000/api/health
```

## API endpoints

| Method | Path | Description | Success |
|---|---|---|---|
| GET | `/api/health` | Health check | 200 |
| GET | `/api/workouts` | List workouts with nested exercises | 200 |
| POST | `/api/workouts` | Create a workout | 201 |
| GET | `/api/workouts/<id>` | Get workout with nested exercise details | 200 |
| DELETE | `/api/workouts/<id>` | Delete workout and its link records | 204 |
| GET | `/api/exercises` | List reusable exercise definitions | 200 |
| POST | `/api/exercises` | Create an exercise definition | 201 |
| GET | `/api/exercises/<id>` | Retrieve exercise by ID | 200 |
| DELETE | `/api/exercises/<id>` | Delete exercise and its link records | 204 |
| POST | `/api/workouts/<id>/exercises` | Attach an exercise with sets/reps and/or duration | 201 |

### Request examples

**Create a workout:**

```bash
curl -i -X POST http://127.0.0.1:5000/api/workouts \
  -H "Content-Type: application/json" \
  -d '{"name":"Leg Day","workout_date":"2026-10-19","notes":"Warm up first"}'
```

**Create a reusable exercise:**

```bash
curl -i -X POST http://127.0.0.1:5000/api/exercises \
  -H "Content-Type: application/json" \
  -d '{"name":"Goblet Squat","category":"strength","description":"Controlled squat"}'
```

**Add the existing exercise to a workout** (replace both IDs with those returned from creation):

```bash
curl -i -X POST http://127.0.0.1:5000/api/workouts/1/exercises \
  -H "Content-Type: application/json" \
  -d '{"exercise_id":1,"sets":3,"reps":12}'
```

**Timed exercise** (instead of sets/reps):

```bash
curl -i -X POST http://127.0.0.1:5000/api/workouts/2/exercises \
  -H "Content-Type: application/json" \
  -d '{"exercise_id":3,"duration_seconds":900}'
```

**Read nested serialization:**

```bash
curl -s http://127.0.0.1:5000/api/workouts/1
```

Sample fragment:

```json
{
  "id": 1,
  "name": "Leg Day",
  "workout_date": "2026-10-19",
  "notes": "Warm up first",
  "workout_exercises": [
    {
      "id": 1,
      "workout_id": 1,
      "exercise_id": 1,
      "sets": 3,
      "reps": 12,
      "duration_seconds": null,
      "exercise": {
        "id": 1,
        "name": "Goblet Squat",
        "category": "strength",
        "description": "Controlled squat"
      }
    }
  ]
}
```

### Validation and API errors

- Names: 3–100 nonblank characters.
- Categories: exactly `strength`, `cardio`, or `mobility`.
- A workout date must be an ISO date in `YYYY-MM-DD` format.
- `notes` and `description`: up to 500 characters.
- Exercise quantities: positive integers; `sets` and `reps` supplied as a pair. Each association needs the pair, `duration_seconds`, or both.
- Association pairs must be unique within a workout; the same exercise can appear in *other* workouts.
- The database additionally enforces named `CHECK`, `UNIQUE`, `NOT NULL`, and foreign-key constraints.

API responses use 200 (GET), 201 (POST), 204 (DELETE), 400 (bad JSON or validation), 404 (missing ID), 405 (unsupported method), 409 (duplicate link/database constraint), and 415 (wrong `Content-Type`).

**Example error:**

```json
{
  "error": "Validation failed.",
  "details": {"category": ["Must be one of: strength, cardio, mobility."]}
}
```

## Testing

```bash
pipenv run pytest -v
pipenv run pytest --cov=app --cov-report=term-missing
```

Tests cover endpoint success and failure paths, reuse and cascade behavior, nested serialization, schema/model validations, `CHECK` constraints, uniqueness and SQLite foreign-key integrity. Fixtures use a fresh in-memory SQLite database for each test.

Continuous integration: `.github/workflows/tests.yml` runs tests for pushes and pull requests.

## File layout

```text
workout-tracker-api/
├── .github/workflows/tests.yml
├── .gitignore
├── Pipfile
├── README.md
├── app/
│   ├── __init__.py            # create_app, DB foreign keys
│   ├── extensions.py          # SQLAlchemy and Migrate extension instances
│   ├── models.py              # ORM entities, relationships, validations, constraints
│   ├── schemas.py             # Marshmallow loading/dumping
│   ├── errors.py              # Consistent JSON error responses
│   └── routes/
│       ├── __init__.py
│       ├── exercises.py
│       ├── helpers.py
│       └── workouts.py
├── config.py                  # DB settings
├── docs/
│   ├── ARCHITECTURE.md
│   └── RUBRIC_CHECKLIST.md
├── migrations/                # Generated by flask db init / migrate
├── pytest.ini
├── seed.py
├── tests/
│   ├── conftest.py
│   ├── test_routes.py
│   ├── test_models.py
│   ├── test_schemas.py
│   └── test_database_constraints.py
└── wsgi.py                    # Flask CLI app entry point
```

## Git / GitHub workflow

Recommended branches and pull requests: `feature/models-and-migrations`, `feature/api-and-validation`, `feature/tests-and-docs`. Commit migration files. Merge PRs into `main`, run tests again, and verify `git status -sb` shows a clean working tree. Submit the full GitHub URL on Canvas.

## Notes on grading

This project implements the requirements present in the lab excerpt (the scenario, task 1, deliverables and 100-point rubric). Canvas Task 2/3 expanders were not included in the supplied text; if they specify *different exact field names, endpoints, or relationships*, align this design with them prior to submission. The grader, not this example implementation, determines the final mark.
