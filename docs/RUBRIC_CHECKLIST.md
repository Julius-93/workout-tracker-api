# 100-point rubric evidence checklist

This file maps each rubric line to demonstrable code and commands. The instructor's marking, not this checklist, determines the grade.

| Rubric category | Pts | Evidence | How to demonstrate |
|---|---:|---|---|
| Endpoints | 10 | `app/routes/workouts.py`, `app/routes/exercises.py` | POST/GET/DELETE and POST attach with curl or pytest |
| Serialization | 10 | `app/schemas.py` | GET `/api/workouts/1` includes nested exercise details |
| Models | 10 | `app/models.py` | Workout, Exercise, WorkoutExercise models with typed fields |
| Relationships | 10 | `app/models.py` | One-to-many from Workout and Exercise to link model, reusable exercises |
| Schema validations | 10 | `app/schemas.py` | `Length`, `Regexp`, `OneOf`, `Range`, `validates_schema` |
| Table constraints | 10 | `app/models.py` | Named `CHECK`, `UNIQUE`, `NOT NULL`, foreign keys; direct SQL tests |
| Model validations | 10 | `app/models.py` | `@validates`: workout name, exercise name/category/description and link measurements |
| Modular code | 10 | app factory, extensions, models, schemas, routes, errors; tests | Clearly separated modules, focused comments |
| README | 10 | `README.md` | Title, description, install, migrations, seed, run, endpoint table |
| Seed file | 5 | `seed.py` | Seeds 2 workouts, 4 exercises, 5 link rows; rerunnable |
| Git workflow | 5 | Your actual GitHub repo | Meaningful commits, 3 branches/PRs merged, clean main history |
| **Total** | **100** | | |

## Final verification

```bash
pipenv run pytest -v
pipenv run pytest --cov=app --cov-report=term-missing
pipenv run flask --app wsgi:app db current
pipenv run python seed.py
git status -sb
git log --oneline --graph --decorate -10
```

Do not claim a 100% grade, green tests or merged PRs unless they actually exist on your own machine and GitHub account. The `migrations/` directory must be generated and committed by the student because database migration versions are environment- and history-specific.
