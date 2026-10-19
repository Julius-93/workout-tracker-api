"""End-to-end HTTP checks for all required routes and error scenarios."""
import pytest


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_initial_lists_are_empty(client):
    assert client.get("/api/workouts").get_json() == []
    assert client.get("/api/exercises").get_json() == []


def test_create_list_get_workout(client, workout_payload):
    created = client.post("/api/workouts", json=workout_payload)
    assert created.status_code == 201
    assert created.get_json()["name"] == "Morning Workout"
    assert created.get_json()["workout_exercises"] == []
    identifier = created.get_json()["id"]
    assert client.get(f"/api/workouts/{identifier}").get_json()["workout_date"] == "2026-10-19"
    assert len(client.get("/api/workouts").get_json()) == 1


def test_create_list_get_exercise(client, exercise_payload):
    created = client.post("/api/exercises", json=exercise_payload)
    assert created.status_code == 201
    identifier = created.get_json()["id"]
    assert client.get(f"/api/exercises/{identifier}").get_json()["category"] == "strength"
    assert len(client.get("/api/exercises").get_json()) == 1


def test_attach_exercise_serializes_nested_relationship(client, entities):
    workout, exercise = entities
    result = client.post(f"/api/workouts/{workout['id']}/exercises", json={
        "exercise_id": exercise["id"], "sets": 3, "reps": 12,
    })
    assert result.status_code == 201
    assert result.get_json()["exercise"]["name"] == "Push-ups"
    nested = client.get(f"/api/workouts/{workout['id']}").get_json()["workout_exercises"]
    assert len(nested) == 1
    assert nested[0]["sets"] == 3
    assert nested[0]["reps"] == 12
    assert nested[0]["exercise"]["category"] == "strength"


def test_duration_only_exercise_works(client, entities):
    workout, exercise = entities
    result = client.post(f"/api/workouts/{workout['id']}/exercises", json={
        "exercise_id": exercise["id"], "duration_seconds": 600,
    })
    assert result.status_code == 201
    assert result.get_json()["duration_seconds"] == 600


def test_reuse_exercise_across_multiple_workouts(client, entities, workout_payload):
    workout, exercise = entities
    second = client.post("/api/workouts", json={**workout_payload, "name": "Second Workout"}).get_json()
    for identifier in (workout["id"], second["id"]):
        response = client.post(f"/api/workouts/{identifier}/exercises", json={
            "exercise_id": exercise["id"], "sets": 2, "reps": 10,
        })
        assert response.status_code == 201


def test_duplicate_association_returns_409(client, entities):
    workout, exercise = entities
    endpoint = f"/api/workouts/{workout['id']}/exercises"
    payload = {"exercise_id": exercise["id"], "sets": 3, "reps": 10}
    assert client.post(endpoint, json=payload).status_code == 201
    assert client.post(endpoint, json=payload).status_code == 409


def test_delete_workout_keeps_exercise_and_cleans_link(client, entities):
    workout, exercise = entities
    client.post(f"/api/workouts/{workout['id']}/exercises", json={
        "exercise_id": exercise["id"], "sets": 2, "reps": 20,
    })
    assert client.delete(f"/api/workouts/{workout['id']}").status_code == 204
    assert client.get(f"/api/workouts/{workout['id']}").status_code == 404
    assert client.get(f"/api/exercises/{exercise['id']}").status_code == 200


def test_delete_exercise_keeps_workout_and_cleans_link(client, entities):
    workout, exercise = entities
    client.post(f"/api/workouts/{workout['id']}/exercises", json={
        "exercise_id": exercise["id"], "duration_seconds": 30,
    })
    assert client.delete(f"/api/exercises/{exercise['id']}").status_code == 204
    result = client.get(f"/api/workouts/{workout['id']}")
    assert result.status_code == 200
    assert result.get_json()["workout_exercises"] == []


def test_missing_resource_404(client):
    for endpoint in ["/api/workouts/999", "/api/exercises/999"]:
        assert client.get(endpoint).status_code == 404


def test_missing_reference_404(client, entities):
    workout, _ = entities
    response = client.post(f"/api/workouts/{workout['id']}/exercises",
                           json={"exercise_id": 999, "sets": 3, "reps": 10})
    assert response.status_code == 404


@pytest.mark.parametrize("payload", [
    {"name": "", "workout_date": "2026-10-19"},
    {"name": "   ", "workout_date": "2026-10-19"},
    {"name": "A" * 101, "workout_date": "2026-10-19"},
    {"name": "Afternoon Workout", "workout_date": "not-a-date"},
    {"workout_date": "2026-10-19"},
])
def test_invalid_workout_payload_400(client, payload):
    response = client.post("/api/workouts", json=payload)
    assert response.status_code == 400
    assert "details" in response.get_json()


@pytest.mark.parametrize("payload", [
    {"name": "AB", "category": "strength"},
    {"name": "Squats", "category": "invalid"},
    {"name": "Squats"},
    {"name": "Squats", "category": "strength", "description": "x" * 501},
])
def test_invalid_exercise_payload_400(client, payload):
    response = client.post("/api/exercises", json=payload)
    assert response.status_code == 400


@pytest.mark.parametrize("bad_fields", [
    {"sets": 3},
    {"reps": 10},
    {"sets": -1, "reps": 10},
    {"duration_seconds": 0},
    {},
])
def test_invalid_association_payload_400(client, entities, bad_fields):
    workout, exercise = entities
    response = client.post(f"/api/workouts/{workout['id']}/exercises",
                           json={"exercise_id": exercise["id"], **bad_fields})
    assert response.status_code == 400


def test_request_must_be_json_object(client):
    assert client.post("/api/exercises", data="hello", content_type="text/plain").status_code == 415
    assert client.post("/api/exercises", json=[1, 2, 3]).status_code == 400


def test_update_endpoints_are_not_implemented(client, entities):
    workout, exercise = entities
    assert client.patch(f"/api/workouts/{workout['id']}", json={"name": "Changed"}).status_code == 405
    assert client.put(f"/api/exercises/{exercise['id']}", json={"name": "Changed"}).status_code == 405
