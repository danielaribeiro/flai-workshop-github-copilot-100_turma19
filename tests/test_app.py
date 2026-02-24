import copy
import pytest

from fastapi.testclient import TestClient

from src import app as fastapi_app_module

client = TestClient(fastapi_app_module.app)

# Keep an unmodified copy of the activities dictionary so tests can reset state
ORIGINAL_ACTIVITIES = copy.deepcopy(fastapi_app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the shared activities dict before each test."""
    fastapi_app_module.activities.clear()
    fastapi_app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_initial_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    # the initial dict should contain at least one known key
    assert "Tennis Club" in data
    assert isinstance(data["Tennis Club"].get("participants"), list)


def test_signup_and_unregister_flow():
    email = "testuser@example.com"
    activity = "Chess Club"

    # sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in fastapi_app_module.activities[activity]["participants"]

    # unregister
    resp2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp2.status_code == 200
    assert email not in fastapi_app_module.activities[activity]["participants"]


def test_signup_duplicate_fails():
    # pick an existing participant
    activity = "Tennis Club"
    existing = ORIGINAL_ACTIVITIES[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "")


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchClub/signup", params={"email": "foo@bar.com"})
    assert resp.status_code == 404


def test_unregister_nonexistent():
    resp = client.post("/activities/NoSuchClub/unregister", params={"email": "foo@bar.com"})
    assert resp.status_code == 404

    # valid activity but non-registered email
    resp2 = client.post("/activities/Tennis Club/unregister", params={"email": "nobody@nowhere.com"})
    assert resp2.status_code == 404
