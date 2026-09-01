from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_all_activities(reset_activities):
    # Arrange
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Drama Club",
        "Art Studio",
        "Math Olympiad",
        "Debate Team",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert set(response_data.keys()) == expected_activity_names
    assert "participants" in response_data["Chess Club"]


def test_signup_for_activity_success(reset_activities):
    # Arrange
    activities["Chess Club"]["participants"] = ["michael@mergington.edu"]
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_duplicate_email_returns_400(reset_activities):
    # Arrange
    activities["Chess Club"]["participants"] = ["michael@mergington.edu"]

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404(reset_activities):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email(reset_activities):
    # Arrange
    activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "daniel@mergington.edu"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered daniel@mergington.edu from Chess Club"
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_404(reset_activities):
    # Arrange
    activities["Chess Club"]["participants"] = ["michael@mergington.edu"]

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "not-here@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
