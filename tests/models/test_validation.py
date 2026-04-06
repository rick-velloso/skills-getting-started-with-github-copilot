"""
Tests for data validation and model constraints.
Verifies input validation and data integrity.
"""

import pytest


@pytest.mark.unit
def test_activity_name_case_sensitivity(client):
    """
    Test that activity names are case-sensitive.
    
    AAA Pattern:
    - Arrange: Prepare activity name in different case
    - Act: Attempt to access activity with different case
    - Assert: Verify 404 for mismatched case
    """
    # ARRANGE
    correct_name = "Chess Club"
    wrong_case_name = "chess club"  # lowercase

    # ACT
    response = client.post(
        f"/activities/{wrong_case_name}/signup",
        params={"email": "test@example.com"}
    )

    # ASSERT
    assert response.status_code == 404, \
        "Activity names should be case-sensitive; 'chess club' should not match 'Chess Club'"
    assert response.json()["detail"] == "Activity not found"


@pytest.mark.unit
def test_email_field_required_for_signup(client):
    """
    Test that email parameter is required for signup.
    
    AAA Pattern:
    - Arrange: Prepare activity name without email
    - Act: Attempt signup without email parameter
    - Assert: Verify request fails with appropriate status
    """
    # ARRANGE
    activity_name = "Chess Club"

    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup"
        # Note: email parameter missing
    )

    # ASSERT
    assert response.status_code == 422, \
        "Missing required email parameter should return validation error (422)"


@pytest.mark.unit
def test_email_field_required_for_unregister(client):
    """
    Test that email parameter is required for unregister.
    
    AAA Pattern:
    - Arrange: Prepare activity name without email
    - Act: Attempt unregister without email parameter
    - Assert: Verify request fails with appropriate status
    """
    # ARRANGE
    activity_name = "Chess Club"

    # ACT
    response = client.post(
        f"/activities/{activity_name}/unregister"
        # Note: email parameter missing
    )

    # ASSERT
    assert response.status_code == 422, \
        "Missing required email parameter should return validation error (422)"


@pytest.mark.unit
def test_empty_email_string(client, sample_activity_name):
    """
    Test that empty email string is accepted (app doesn't validate format).
    
    AAA Pattern:
    - Arrange: Prepare empty email string
    - Act: Attempt signup with empty email
    - Assert: Verify request is accepted (no format validation currently)
    """
    # ARRANGE
    activity_name = sample_activity_name
    empty_email = ""

    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": empty_email}
    )

    # ASSERT
    # Note: Current implementation doesn't validate email format
    # This test documents current behavior; constraint should be added later
    assert response.status_code == 200, \
        "Currently app accepts empty email (TODO: Add email format validation)"


@pytest.mark.unit
def test_activity_data_structure_consistency(client):
    """
    Test that all activities have consistent data structure.
    
    AAA Pattern:
    - Arrange: Define required fields per activity
    - Act: Fetch all activities
    - Assert: Verify all required fields present and types correct
    """
    # ARRANGE
    required_fields = {
        "description": str,
        "schedule": str,
        "max_participants": int,
        "participants": list
    }

    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT
    for activity_name, activity in activities.items():
        for field_name, field_type in required_fields.items():
            assert field_name in activity, \
                f"Activity '{activity_name}' missing field '{field_name}'"
            assert isinstance(activity[field_name], field_type), \
                f"Activity '{activity_name}' field '{field_name}' should be {field_type}, " \
                f"got {type(activity[field_name])}"


@pytest.mark.unit
def test_participants_list_all_strings(client):
    """
    Test that participants list contains only string values (emails).
    
    AAA Pattern:
    - Arrange: Fetch activities
    - Act: Iterate through all participants of all activities
    - Assert: Verify all participants are strings
    """
    # ARRANGE
    # (participants should be list of email strings)

    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT
    for activity_name, activity in activities.items():
        participants = activity["participants"]
        for participant in participants:
            assert isinstance(participant, str), \
                f"In activity '{activity_name}': participant '{participant}' " \
                f"should be string, got {type(participant)}"


@pytest.mark.unit
def test_max_participants_is_positive_integer(client):
    """
    Test that max_participants field contains positive integer values.
    
    AAA Pattern:
    - Arrange: Fetch activities
    - Act: Check max_participants value for each activity
    - Assert: Verify all max_participants are positive integers
    """
    # ARRANGE
    # (max_participants should be positive integers)

    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT
    for activity_name, activity in activities.items():
        max_participants = activity["max_participants"]
        assert isinstance(max_participants, int), \
            f"In activity '{activity_name}': max_participants should be int"
        assert max_participants > 0, \
            f"In activity '{activity_name}': max_participants should be positive, " \
            f"got {max_participants}"
