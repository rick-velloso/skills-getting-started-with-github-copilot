"""
Tests for POST /activities/{activity_name}/signup endpoint
Verifies student signup functionality with various scenarios.
"""

import pytest


@pytest.mark.unit
def test_signup_success(client, sample_activity_name, sample_email):
    """
    Test successful student signup for an activity.
    
    AAA Pattern:
    - Arrange: Prepare activity name and student email
    - Act: Send POST signup request
    - Assert: Verify 200 status, confirmation message, and participant added
    """
    # ARRANGE
    activity_name = sample_activity_name
    email = sample_email

    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # ASSERT
    assert response.status_code == 200, "Expected successful signup (200)"
    data = response.json()
    assert "message" in data, "Response should contain message"
    assert email in data["message"], f"Message should mention {email}"
    assert activity_name in data["message"], f"Message should mention {activity_name}"
    
    # Verify participant was actually added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"], \
        "Participant should be added to activity list"


@pytest.mark.unit
def test_signup_duplicate_email(client, sample_activity_name):
    """
    Test that duplicate signup returns 400 error.
    
    AAA Pattern:
    - Arrange: Use email already in activity participants
    - Act: Attempt signup with existing participant
    - Assert: Verify 400 status and appropriate error message
    """
    # ARRANGE
    activity_name = sample_activity_name
    # Michael is already in Chess Club per original_activities
    existing_email = "michael@mergington.edu"

    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )

    # ASSERT
    assert response.status_code == 400, \
        "Expected bad request (400) for duplicate signup"
    error_detail = response.json()
    assert error_detail["detail"] == "Student already signed up for this activity", \
        "Expected specific error message for duplicate signup"


@pytest.mark.unit
def test_signup_activity_not_found(client, sample_email):
    """
    Test that signup to non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Use non-existent activity name
    - Act: Attempt signup for missing activity
    - Assert: Verify 404 status and activity not found message
    """
    # ARRANGE
    nonexistent_activity = "Nonexistent Club"
    email = sample_email

    # ACT
    response = client.post(
        f"/activities/{nonexistent_activity}/signup",
        params={"email": email}
    )

    # ASSERT
    assert response.status_code == 404, \
        "Expected not found (404) for nonexistent activity"
    error_detail = response.json()
    assert error_detail["detail"] == "Activity not found", \
        "Expected 'Activity not found' error message"


@pytest.mark.unit
def test_signup_multiple_students_same_activity(client, sample_activity_name, all_sample_emails):
    """
    Test multiple different students can signup for same activity.
    
    AAA Pattern:
    - Arrange: Prepare multiple unique emails
    - Act: Signup each student for activity in sequence
    - Assert: Verify all signups succeed and all participants are added
    """
    # ARRANGE
    activity_name = sample_activity_name
    emails = all_sample_emails[:3]  # Use first 3 emails

    # ACT & ASSERT for each signup
    for i, email in enumerate(emails):
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT each signup succeeds
        assert response.status_code == 200, \
            f"Signup {i+1} should succeed for email {email}"

    # Final ASSERT: Verify all participants are in activity
    activities_response = client.get("/activities")
    activities = activities_response.json()
    activity_participants = activities[activity_name]["participants"]
    
    for email in emails:
        assert email in activity_participants, \
            f"Email {email} should be in activity participants"


@pytest.mark.unit
def test_signup_response_message_format(client, sample_activity_name, sample_email):
    """
    Test that signup response message has correct format and content.
    
    AAA Pattern:
    - Arrange: Prepare test data
    - Act: Send signup request
    - Assert: Verify response message format contains key information
    """
    # ARRANGE
    activity_name = sample_activity_name
    email = sample_email

    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    data = response.json()

    # ASSERT
    assert response.status_code == 200, "Expected successful response"
    assert "message" in data, "Response should have 'message' key"
    message = data["message"]
    assert email in message, f"Message must contain email {email}"
    assert activity_name in message, f"Message must contain activity {activity_name}"
    assert "Signed up" in message or "signed up" in message.lower(), \
        "Message should indicate signup action"
