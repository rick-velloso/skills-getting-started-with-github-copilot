"""
Tests for the root endpoint (GET /)
Verifies redirect behavior to static files.
"""

import pytest


@pytest.mark.unit
def test_root_redirect(client):
    """
    Test that root endpoint redirects to static index.html page.
    
    AAA Pattern:
    - Arrange: Initialize test client (from fixture)
    - Act: Send GET request to root endpoint
    - Assert: Verify redirect status code and location header
    """
    # ARRANGE
    expected_redirect_url = "/static/index.html"

    # ACT
    response = client.get("/", follow_redirects=False)

    # ASSERT
    assert response.status_code == 307, "Expected temporary redirect (307) status code"
    assert response.headers["location"] == expected_redirect_url, \
        f"Expected redirect to {expected_redirect_url}"


@pytest.mark.unit
def test_root_redirect_with_follow(client):
    """
    Test root endpoint redirect by following it to verify static file is accessible.
    
    AAA Pattern:
    - Arrange: Initialize test client (from fixture)
    - Act: Send GET request to root endpoint with follow_redirects=True
    - Assert: Verify final response status is 200 (success)
    """
    # ARRANGE
    # (client fixture provides TestClient)

    # ACT
    response = client.get("/", follow_redirects=True)

    # ASSERT
    assert response.status_code == 200, "Expected successful response after redirect"
