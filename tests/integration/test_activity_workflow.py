"""
Integration tests for multi-step activity workflows.
Verifies realistic user scenarios spanning multiple endpoints.
"""

import pytest


@pytest.mark.integration
def test_complete_activity_workflow_signup_view_unregister(client, sample_email):
    """
    Test realistic workflow: get activities > signup > verify signup > unregister.
    
    AAA Pattern:
    - Arrange: Prepare test email and activity name
    - Act: Execute complete workflow (get, signup, get, unregister)
    - Assert: Verify each step succeeds and data changes appropriately
    """
    # ARRANGE
    activity_name = "Yoga Club"
    email = sample_email

    # Get initial state
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"].copy()
    assert email not in initial_participants, \
        "Test email should not be pre-enrolled"

    # ACT: Step 1 - View all activities
    view_response = client.get("/activities")
    assert view_response.status_code == 200, "Initial /activities request should succeed"

    # ACT: Step 2 - Signup for activity
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200, f"Signup for {activity_name} should succeed"

    # ASSERT: Step 2 - Verify signup
    assert "message" in signup_response.json()
    assert email in signup_response.json()["message"]

    # ACT: Step 3 - View activities again (verify signup persisted)
    verify_response = client.get("/activities")
    assert verify_response.status_code == 200, "Follow-up /activities request should succeed"
    participants_after_signup = verify_response.json()[activity_name]["participants"]
    assert email in participants_after_signup, \
        f"Email {email} should be in participants after signup"

    # ACT: Step 4 - Unregister from activity
    unregister_response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200, \
        f"Unregister from {activity_name} should succeed"

    # ASSERT: Step 4 - Verify unregister completed
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    assert email not in final_participants, \
        f"Email {email} should not be in participants after unregister"


@pytest.mark.integration
def test_multiple_students_signup_same_activity(client, all_sample_emails):
    """
    Test multiple students can independently signup/unregister from same activity.
    
    AAA Pattern:
    - Arrange: Prepare multiple email addresses and activity
    - Act: Each student signs up, views activities, unregisters
    - Assert: Verify all operations succeed and final state is clean
    """
    # ARRANGE
    activity_name = "Art Club"
    emails = all_sample_emails

    # ACT: All students sign up
    for email in emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # ASSERT each signup succeeds
        assert response.status_code == 200, \
            f"Signup for {email} should succeed"

    # ASSERT: All students are enrolled
    activities = client.get("/activities").json()
    for email in emails:
        assert email in activities[activity_name]["participants"], \
            f"{email} should be enrolled in {activity_name}"

    # ACT: Remove students one by one
    for i, email in enumerate(emails):
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        # ASSERT unregister succeeds
        assert response.status_code == 200, \
            f"Unregister for {email} should succeed"

        # ASSERT: Student removed, others still present
        activities = client.get("/activities").json()
        remaining_emails = emails[i+1:]
        assert email not in activities[activity_name]["participants"], \
            f"{email} should be removed after unregister"
        for other_email in remaining_emails:
            assert other_email in activities[activity_name]["participants"], \
                f"{other_email} should still be enrolled"


@pytest.mark.integration
def test_workflow_with_error_handling(client, sample_email):
    """
    Test workflow that includes error conditions and recovery.
    
    AAA Pattern:
    - Arrange: Prepare test data
    - Act: Attempt invalid operations followed by valid ones
    - Assert: Verify errors are handled and valid operations still work
    """
    # ARRANGE
    activity_name = "Drama Club"
    email = sample_email
    wrong_activity = "Nonexistent Club"

    # ACT: Step 1 - Try signup to wrong activity (should fail)
    wrong_response = client.post(
        f"/activities/{wrong_activity}/signup",
        params={"email": email}
    )
    # ASSERT: Expected error
    assert wrong_response.status_code == 404, \
        "Signup to nonexistent activity should return 404"

    # ACT: Step 2 - Signup to correct activity (should succeed)
    correct_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    # ASSERT: Success
    assert correct_response.status_code == 200, \
        "Signup to correct activity should succeed"

    # ACT: Step 3 - Try duplicate signup (should fail)
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    # ASSERT: Expected error
    assert duplicate_response.status_code == 400, \
        "Duplicate signup should return 400"

    # ACT: Step 4 - Unregister and verify clean state
    unregister_response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    # ASSERT: Success
    assert unregister_response.status_code == 200, \
        "Unregister should succeed"

    # Verify clean state
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"], \
        "Participant list should be clean after unregister"


@pytest.mark.integration
def test_workflow_signup_same_participant_different_activities(client, sample_email):
    """
    Test that one student can signup to multiple different activities.
    
    AAA Pattern:
    - Arrange: Prepare student email and multiple activities
    - Act: Signup to multiple activities and verify each
    - Assert: Student appears in all activity participant lists
    """
    # ARRANGE
    email = sample_email
    activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]

    # ACT: Signup to first activity
    for activity_name in activities_to_join:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # ASSERT each signup succeeds
        assert response.status_code == 200, \
            f"Signup to {activity_name} should succeed"

    # ASSERT: Verify student is in all activities
    activities = client.get("/activities").json()
    for activity_name in activities_to_join:
        assert email in activities[activity_name]["participants"], \
            f"{email} should be participant in {activity_name}"

    # ACT: Unregister from some activities
    for activity_name in activities_to_join[:2]:  # First 2 activities
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        # ASSERT unregister succeeds
        assert response.status_code == 200, \
            f"Unregister from {activity_name} should succeed"

    # ASSERT: Verify final state
    final_activities = client.get("/activities").json()
    for activity_name in activities_to_join[:2]:
        assert email not in final_activities[activity_name]["participants"], \
            f"{email} should not be in {activity_name} after unregister"
    
    assert email in final_activities[activities_to_join[2]]["participants"], \
        f"{email} should still be in {activities_to_join[2]}"
