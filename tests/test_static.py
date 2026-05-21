"""
Integration tests for static file routing.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test conditions and fixtures
- Act: Execute the API call being tested
- Assert: Verify the response status and behavior
"""

from fastapi.testclient import TestClient


class TestStaticRouting:
    """Tests for static file routing"""

    def test_root_redirects_to_index_html(self, client):
        """
        Test that GET / redirects to /static/index.html.

        Arrange: Have a test client ready
        Act: Call GET / with follow_redirects=False to capture the redirect
        Assert: Verify response is 307 with correct Location header
        """
        # Arrange
        # (none needed)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follows_to_index_html(self, client):
        """
        Test that following the redirect from GET / reaches the HTML file.

        Arrange: Have a test client ready
        Act: Call GET / with follow_redirects=True
        Assert: Verify final response contains HTML content
        """
        # Arrange
        # (none needed)

        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # Verify the response contains HTML content
        assert "text/html" in response.headers.get("content-type", "")
