"""
Integration tests for the Mergington High School API activities endpoints.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test conditions and fixtures
- Act: Execute the API call being tested
- Assert: Verify the response status, data, and side effects
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, activity_names):
        """
        Test that GET /activities returns all 9 pre-seeded activities.

        Arrange: Have a test client ready with default data
        Act: Call GET /activities
        Assert: Verify response status is 200 and contains all activities
        """
        # Arrange
        expected_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_count
        for activity_name in activity_names:
            assert activity_name in activities

    def test_get_activities_returns_correct_structure(self, client):
        """
        Test that each activity has the expected data structure.

        Arrange: Have a test client ready
        Act: Call GET /activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_strings(self, client):
        """
        Test that participants in each activity are email strings.

        Arrange: Have a test client ready
        Act: Call GET /activities
        Assert: Verify participants are valid strings
        """
        # Arrange
        # (none needed)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """
        Test that a student can successfully sign up for an activity.

        Arrange: Prepare test client with a new email and activity
        Act: POST signup request with email parameter
        Assert: Verify response is 200 and student is added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "test_student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify the student was added by checking the activity
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_signup_already_signed_up(self, client):
        """
        Test that signing up twice for the same activity returns 400 error.

        Arrange: Sign up a student once
        Act: Attempt to sign up the same student again
        Assert: Verify response is 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in pre-seeded data

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_activity_not_found(self, client):
        """
        Test that signing up for a non-existent activity returns 404.

        Arrange: Prepare request for non-existent activity
        Act: POST signup request with invalid activity name
        Assert: Verify response is 404 with "Activity not found" message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test_student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_students_same_activity(self, client):
        """
        Test that multiple different students can sign up for the same activity.

        Arrange: Prepare two unique emails
        Act: Sign up both students sequentially
        Assert: Verify both are added to participants
        """
        # Arrange
        activity_name = "Programming Class"
        email1 = "new_student_1@mergington.edu"
        email2 = "new_student_2@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client):
        """
        Test that a student can successfully unregister from an activity.

        Arrange: Prepare test client and use a pre-seeded participant
        Act: DELETE signup request with email of existing participant
        Assert: Verify response is 200 and student is removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Pre-seeded participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify the student was removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_student_not_signed_up(self, client):
        """
        Test that unregistering a student who isn't signed up returns 400.

        Arrange: Prepare request with email not in activity participants
        Act: DELETE signup request for student not in activity
        Assert: Verify response is 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "not_signed_up@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_activity_not_found(self, client):
        """
        Test that unregistering from a non-existent activity returns 404.

        Arrange: Prepare request for non-existent activity
        Act: DELETE signup request with invalid activity name
        Assert: Verify response is 404 with "Activity not found" message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test_student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_then_unregister(self, client):
        """
        Test the full signup then unregister flow for a student.

        Arrange: Prepare test client with new email
        Act: Sign up a student, then unregister the same student
        Assert: Verify both operations succeed and participant list is correct
        """
        # Arrange
        activity_name = "Art Club"
        email = "test_flow@mergington.edu"
        
        # Get initial participant count
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Sign up successful
        assert signup_response.status_code == 200
        after_signup_activities = client.get("/activities").json()
        assert len(after_signup_activities[activity_name]["participants"]) == initial_count + 1
        assert email in after_signup_activities[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Unregister successful
        assert unregister_response.status_code == 200
        final_activities = client.get("/activities").json()
        assert len(final_activities[activity_name]["participants"]) == initial_count
        assert email not in final_activities[activity_name]["participants"]
