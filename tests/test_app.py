"""
Tests for the Mergington High School Activities API

Tests all endpoints including GET activities, POST signup, and DELETE unregister.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the varsity soccer team for training and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim laps and compete in swim meets",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art mediums including painting and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lily@mergington.edu"]
        },
        "Drama Club": {
            "description": "Participate in theatrical productions and improve acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and conduct experiments",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "liam@mergington.edu"]
        }
    }
    
    # Reset to original state before each test
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test (optional)
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Signed up test@mergington.edu for Chess Club"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        assert "test@mergington.edu" in activities_response.json()["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_duplicate_signup(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_for_full_activity(self, client):
        """Test signing up for an activity that is already full"""
        # Fill up Chess Club (max 12 participants)
        current_participants = len(activities["Chess Club"]["participants"])
        spots_left = activities["Chess Club"]["max_participants"] - current_participants
        
        # Add participants until full
        for i in range(spots_left):
            response = client.post(f"/activities/Chess Club/signup?email=student{i}@mergington.edu")
            assert response.status_code == 200
        
        # Next signup should fail
        response = client.post("/activities/Chess Club/signup?email=overflow@mergington.edu")
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successfully unregistering from an activity"""
        email = "michael@mergington.edu"
        
        # Verify participant exists
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from Chess Club"
        
        # Verify participant was removed
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_registered_student(self, client):
        """Test unregistering a student who is not registered"""
        email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_and_signup_again(self, client):
        """Test that a student can unregister and then sign up again"""
        email = "flexible@mergington.edu"
        
        # Sign up
        response1 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(f"/activities/Soccer Team/unregister?email={email}")
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify participant is in the list once
        assert activities["Soccer Team"]["participants"].count(email) == 1


class TestIntegrationScenarios:
    """Integration tests for realistic user scenarios"""
    
    def test_student_joins_multiple_activities(self, client):
        """Test a student joining multiple different activities"""
        email = "busy@mergington.edu"
        
        # Join multiple activities
        activities_to_join = ["Chess Club", "Programming Class", "Art Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
    
    def test_activity_capacity_management(self, client):
        """Test that activity capacity is properly managed"""
        activity = "Debate Team"
        max_capacity = activities[activity]["max_participants"]
        current_count = len(activities[activity]["participants"])
        available_spots = max_capacity - current_count
        
        # Fill remaining spots
        for i in range(available_spots):
            response = client.post(
                f"/activities/{activity}/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Verify activity is full
        all_activities = client.get("/activities").json()
        assert len(all_activities[activity]["participants"]) == max_capacity
        
        # Try to add one more (should fail)
        response = client.post(
            f"/activities/{activity}/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
