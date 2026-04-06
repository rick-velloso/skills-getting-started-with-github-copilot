"""
Tests for POST /activities/{activity_name}/unregister endpoint
Verifies student unregistration functionality with various scenarios.
"""

import pytest


@pytest.mark.unit
def test_unregister_success(client, sample_activity_name):
    """
    Test successful student unregistration from an activity.
    
    AAA Pattern:
    - Arrange: Use existing participant in activity
    - Act: Send POST unregister request
    - Assert: Verify 200 status and participant removed from list
    """
    # ARRANGE
    activity_name = sample_activity_name
    # Michael is in Chess Club per original_activities
    existing_email = "michael@mergington.edu"

    # Verify participant is in activity before unregister
    activities_before = client.get("/activities").json()
    assert existing_email in activities_before[activity_name]["participants"], \
        "Participant should be in activity before unregister test"

    # ACT
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": existing_email}
    )

    # ASSERT
    assert response.status_code == 200, "Expected successful unregister (200)"
    data = response.json()
    assert "message" in data, "Response should contain message"
    assert existing_email in data["message"], \
        f"Message should mention {existing_email}"
    
    # Verify participant was actually removed
    activities_after = client.get("/activities").json()
    assert existing_email not in activities_after[activity_name]["participants"], \
        "Participant should be removed from activity list"


@pytest.mark.unit
def test_unregister_not_registered(client, sample_activity_name, sample_email):
    """
    Test that unregistering non-existent participant returns 400.
    
    AAA Pattern:
    - Arrange: Use email not in activity participants
    - Act: Attempt unregister for non-participant
    - Assert: Verify 400 status and appropriate error message
    """
    # ARRANGE
    activity_name = sample_activity_name
    email = sample_email  # This email is NOT in Chess Club

    # ACT
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    # ASSERT
    assert response.status_code == 400, \
        "Expected bad request (400) for unregistering non-participant"
    error_detail = response.json()
    assert error_detail["detail"] == "Student is not signed up for this activity", \
        "Expected specific error message for non-participant"


@pytest.mark.unit
def test_unregister_activity_not_found(client, sample_email):
    """
    Test that unregister from non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Use non-existent activity name
    - Act: Attempt unregister from missing activity
    - Assert: Verify 404 status and activity not found message
    """
    # ARRANGE
    nonexistent_activity = "Nonexistent Club"
    email = sample_email

    # ACT
    response = client.post(
        f"/activities/{nonexistent_activity}/unregister",
        params={"email": email}
    )

    # ASSERT
    assert response.status_code == 404, \
        "Expected not found (404) for nonexistent activity"
    error_detail = response.json()
    assert error_detail["detail"] == "Activity not found", \
        "Expected 'Activity not found' error message"


@pytest.mark.unit
def test_unregister_response_message_format(client, sample_activity_name):
    """
    Test that unregister response message has correct format and content.
    
    AAA Pattern:
    - Arrange: Prepare existing participant data
    - Act: Send unregister request
    - Assert: Verify response message format contains key information
    """
    # ARRANGE
    activity_name = sample_activity_name
    existing_email = "daniel@mergington.edu"  # Second participant in Chess Club

    # ACT
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": existing_email}
    )
    data = response.json()

    # ASSERT
    assert response.status_code == 200, "Expected successful response"
    assert "message" in data, "Response should have 'message' key"
    message = data["message"]
    assert existing_email in message, f"Message must contain email {existing_email}"
    assert activity_name in message, f"Message must contain activity {activity_name}"
    assert "Unregistered" in message or "unregistered" in message.lower(), \
        "Message should indicate unregister action"


@pytest.mark.unit
def test_unregister_then_signup_again(client, sample_activity_name):
    """
    Test that student can signup again after unregistering from activity.
    
    AAA Pattern:
    - Arrange: Identify participant and activity
    - Act: Unregister participant, then signup again
    - Assert: Verify both operations succeed and participant is re-added
    """
    # ARRANGE
    activity_name = sample_activity_name
    email = "michael@mergington.edu"

    # ACT: Unregister
    unregister_response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    # ASSERT unregister succeeds
    assert unregister_response.status_code == 200, \
        "Unregister should succeed"

    # ACT: Signup again
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # ASSERT signup succeeds and participant is back
    assert signup_response.status_code == 200, \
        "Re-signup should succeed"
    
    activities_final = client.get("/activities").json()
    assert email in activities_final[activity_name]["participants"], \
        "Participant should be in activity after re-signup"


@pytest.mark.unit
def test_unregister_one_of_many_participants(client, sample_activity_name):
    """
    Test unregistering one participant doesn't affect other participants.
    
    AAA Pattern:
    - Arrange: Get list of participants before unregister
    - Act: Unregister one participant
    - Assert: Verify only that participant removed, others remain
    """
    # ARRANGE
    activity_name = sample_activity_name
    activities_before = client.get("/activities").json()
    participants_before = activities_before[activity_name]["participants"].copy()
    email_to_remove = participants_before[0]
    other_participants = participants_before[1:]

    # ACT
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email_to_remove}
    )

    # ASSERT
    assert response.status_code == 200, "Unregister should succeed"
    
    activities_after = client.get("/activities").json()
    participants_after = activities_after[activity_name]["participants"]
    
    assert email_to_remove not in participants_after, \
        "Removed participant should not be in list"
    for other_email in other_participants:
        assert other_email in participants_after, \
            f"Other participant {other_email} should still be in list"
