"""
Tests for GET /activities endpoint
Verifies retrieval of all activities and response structure.
"""

import pytest


@pytest.mark.unit
def test_get_activities_success(client):
    """
    Test that GET /activities returns all activities successfully.
    
    AAA Pattern:
    - Arrange: Prepare expected activities count
    - Act: Send GET request to /activities endpoint
    - Assert: Verify response status 200 and activities data present
    """
    # ARRANGE
    expected_activities_count = 9  # Number of activities in original_activities

    # ACT
    response = client.get("/activities")

    # ASSERT
    assert response.status_code == 200, "Expected successful response"
    activities = response.json()
    assert len(activities) == expected_activities_count, \
        f"Expected {expected_activities_count} activities, got {len(activities)}"


@pytest.mark.unit
def test_get_activities_structure(client):
    """
    Test that GET /activities returns proper structure for each activity.
    
    AAA Pattern:
    - Arrange: Identify required activity fields
    - Act: Send GET request and retrieve first activity
    - Assert: Verify all required fields present in response
    """
    # ARRANGE
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT
    assert len(activities) > 0, "Activities list should not be empty"
    first_activity = list(activities.values())[0]
    for field in required_fields:
        assert field in first_activity, \
            f"Missing required field '{field}' in activity structure"


@pytest.mark.unit
def test_get_activities_participants_list(client):
    """
    Test that each activity contains a participants list with emails.
    
    AAA Pattern:
    - Arrange: Identify a known activity and its participants
    - Act: Fetch activities and extract specific activity
    - Assert: Verify participants are present and are strings (emails)
    """
    # ARRANGE
    known_activity = "Chess Club"
    expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT
    assert known_activity in activities, f"Expected activity '{known_activity}' in response"
    activity = activities[known_activity]
    assert isinstance(activity["participants"], list), \
        "Participants should be a list"
    assert activity["participants"] == expected_participants, \
        f"Expected participants {expected_participants}, got {activity['participants']}"


@pytest.mark.unit
def test_get_activities_response_type(client):
    """
    Test that GET /activities returns a dictionary (object) not a list.
    
    AAA Pattern:
    - Arrange: Know expected response type
    - Act: Fetch activities
    - Assert: Verify response is dictionary with activity names as keys
    """
    # ARRANGE
    # (response should be dict with activity_name as keys)

    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT
    assert isinstance(activities, dict), \
        "Activities should be returned as a dictionary"
    assert all(isinstance(name, str) for name in activities.keys()), \
        "Activity names should be strings"
