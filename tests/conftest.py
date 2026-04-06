"""
Shared pytest fixtures for FastAPI application tests.
Provides TestClient, sample data, and test utilities.
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app
import src.app

# Create a deep copy of original activities at module load time
# This ensures we have an unmodified reference for resetting tests
_ORIGINAL_ACTIVITIES = None


@pytest.fixture
def client():
    """
    Provides a TestClient for testing FastAPI endpoints.
    
    Yields:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Automatically resets activities to original state before each test.
    This ensures test isolation and prevents side effects between tests.
    
    Yields:
        None
    """
    global _ORIGINAL_ACTIVITIES
    
    # On first run, save the original activities before any test modifies them
    if _ORIGINAL_ACTIVITIES is None:
        _ORIGINAL_ACTIVITIES = deepcopy(src.app.activities)
    
    # Reset activities before test
    src.app.activities.clear()
    src.app.activities.update(deepcopy(_ORIGINAL_ACTIVITIES))
    
    # Test runs here
    yield
    
    # Reset activities after test too (for cleanliness)
    src.app.activities.clear()
    src.app.activities.update(deepcopy(_ORIGINAL_ACTIVITIES))


@pytest.fixture
def sample_activity_name():
    """
    Provides a sample activity name for testing.
    
    Returns:
        str: Activity name that exists in the test database
    """
    return "Chess Club"


@pytest.fixture
def sample_email():
    """
    Provides a sample email for testing signup/unregister operations.
    
    Returns:
        str: Email address in realistic format
    """
    return "test.student@mergington.edu"


@pytest.fixture
def existing_activity_with_participants():
    """
    Provides details of an activity that already has participants.
    
    Returns:
        dict: Contains activity_name and list of existing participants
    """
    return {
        "activity_name": "Chess Club",
        "existing_participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    }


@pytest.fixture
def all_sample_emails():
    """
    Provides multiple sample emails for testing multiple signups/operations.
    
    Returns:
        list: List of unique email addresses
    """
    return [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu",
        "student4@mergington.edu"
    ]
