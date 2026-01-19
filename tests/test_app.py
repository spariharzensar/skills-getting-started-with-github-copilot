import pytest
from fastapi.testclient import TestClient


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check that Chess Club exists and has expected structure
    assert "Chess Club" in activities
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client: TestClient):
    """Test successful signup for an activity"""
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert "test@mergington.edu" in result["message"]
    assert "Chess Club" in result["message"]


def test_signup_for_activity_already_signed_up(client: TestClient):
    """Test signup when student is already signed up"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")

    # Try to signup again
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_for_nonexistent_activity(client: TestClient):
    """Test signup for an activity that doesn't exist"""
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_unregister_from_activity_success(client: TestClient):
    """Test successful unregistration from an activity"""
    # First signup
    client.post("/activities/Tennis%20Club/signup?email=unregister@mergington.edu")

    # Then unregister
    response = client.delete("/activities/Tennis%20Club/participants/unregister@mergington.edu")
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert "unregister@mergington.edu" in result["message"]
    assert "Tennis Club" in result["message"]


def test_unregister_from_activity_not_signed_up(client: TestClient):
    """Test unregistration when student is not signed up"""
    response = client.delete("/activities/Chess%20Club/participants/notsignedup@mergington.edu")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert "not signed up" in result["detail"]


def test_unregister_from_nonexistent_activity(client: TestClient):
    """Test unregistration from an activity that doesn't exist"""
    response = client.delete("/activities/Nonexistent%20Activity/participants/test@mergington.edu")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_root_redirect(client: TestClient):
    """Test root endpoint redirects to static index"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]