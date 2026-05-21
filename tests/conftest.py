"""
Shared test configuration and fixtures for the FastAPI test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for making test requests.
    
    Each test gets a fresh application instance to avoid data pollution
    between tests. The client is function-scoped, so each test starts with
    the original pre-seeded activities data.
    
    Yields:
        TestClient: A test client configured for the FastAPI app
    """
    # Create a fresh app instance for each test
    test_client = TestClient(app)
    yield test_client


@pytest.fixture
def activity_names():
    """
    Fixture that provides the list of pre-seeded activity names.
    
    Yields:
        list: Names of all activities available in the test app
    """
    yield [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Art Club",
        "Drama Club",
        "Math Club",
        "Robotics Club"
    ]
