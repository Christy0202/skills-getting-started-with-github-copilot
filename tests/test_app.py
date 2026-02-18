"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original_activities = {
        "Basketball": {
            "description": "Team basketball practice and friendly matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills development and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater, acting, and stage performance",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore experiments and scientific discoveries",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["isabella@mergington.edu", "ethan@mergington.edu"]
        },
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
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 9
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert data["Basketball"]["description"] == "Team basketball practice and friendly matches"
    
    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in activities["Basketball"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/NonexistentClub/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        # First signup
        response = client.post(
            "/activities/Basketball/signup?email=james@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        student = "multi@mergington.edu"
        
        response1 = client.post(
            f"/activities/Basketball/signup?email={student}"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            f"/activities/Tennis%20Club/signup?email={student}"
        )
        assert response2.status_code == 200
        
        assert student in activities["Basketball"]["participants"]
        assert student in activities["Tennis Club"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        student = "james@mergington.edu"
        
        response = client.delete(
            f"/activities/Basketball/unregister?email={student}"
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert student not in activities["Basketball"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/NonexistentClub/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_signed_up(self, client, reset_activities):
        """Test unregistering a student who isn't signed up"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notstudent@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        student = "newstudent@mergington.edu"
        activity = "Basketball"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup?email={student}"
        )
        assert response1.status_code == 200
        assert student in activities[activity]["participants"]
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/unregister?email={student}"
        )
        assert response2.status_code == 200
        assert student not in activities[activity]["participants"]
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup?email={student}"
        )
        assert response3.status_code == 200
        assert student in activities[activity]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client, reset_activities):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
