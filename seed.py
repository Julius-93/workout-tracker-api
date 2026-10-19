"""DEVELOPMENT ONLY: resets and seeds all three models with reusable exercises.

Usage after applying migrations: pipenv run python seed.py
NOTE: clears all existing workout and exercise data in the configured DB!
"""
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import Exercise, Workout, WorkoutExercise


def seed():
    app = create_app()
    with app.app_context():
        # Purge association rows first to comply with foreign key constraints.
        db.session.query(WorkoutExercise).delete()
        db.session.query(Workout).delete()
        db.session.query(Exercise).delete()
        db.session.commit()

        pushups = Exercise(name="Push-ups", category="strength",
                           description="Upper-body bodyweight exercise")
        squats = Exercise(name="Squats", category="strength",
                          description="Compound leg exercise")
        running = Exercise(name="Running", category="cardio",
                           description="Steady-state cardio exercise")
        stretching = Exercise(name="Stretching", category="mobility",
                              description="Full-body mobility routine")

        morning = Workout(name="Morning Strength", workout_date=date.today(),
                          notes="Complete three rounds")
        evening = Workout(name="Evening Cardio", workout_date=date.today() + timedelta(days=1),
                          notes="Keep breathing steady")

        db.session.add_all([pushups, squats, running, stretching, morning, evening])
        db.session.flush()
        db.session.add_all([
            WorkoutExercise(workout=morning, exercise=pushups, sets=3, reps=12),
            WorkoutExercise(workout=morning, exercise=squats, sets=3, reps=15),
            WorkoutExercise(workout=evening, exercise=running, duration_seconds=1200),
            WorkoutExercise(workout=evening, exercise=stretching, duration_seconds=600),
            WorkoutExercise(workout=evening, exercise=squats, sets=2, reps=15),
        ])
        db.session.commit()
        print("Seeded 2 workouts, 4 exercises and 5 workout-exercise links.")


if __name__ == "__main__":
    seed()
