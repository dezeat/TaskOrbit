"""Integration tests for authentication routes.

These tests exercise the real HTTP endpoints (registered on the app
blueprint) using a test client and an in-memory database. They verify
that registration and login flows behave as expected:

- Successful registration followed by login returns a redirect to the
  home page (status 302).
- Failed login attempts (unknown user or wrong password) return a 200
  response with an error message rendered in the login template.

We run these as integration tests to confirm that route handlers,
templates, sessions, and DB interactions work together.
"""

import pytest
from flask.testing import FlaskClient


@pytest.mark.usefixtures("fix_app")
class TestAuthRoutes:
    """Group of integration tests covering authentication routes.

    What: Exercises the `/register` and `/login` endpoints using a
    test client and an in-memory database.

    Why: Confirms that the full request handling stack (routes,
    templates, session handling, and DB persistence) integrates
    correctly for common authentication flows.
    """

    def test_login_success(self, fix_client: FlaskClient) -> None:
        """Register a new user and ensure login redirects to home.

        What: POST `/register` then POST `/login` with same credentials.
        Why: Ensures successful registration produces a user that can
        authenticate and that the app redirects to the expected page on
        success.
        """
        fix_client.post("/register", data={"username": "new", "password": "pwd12345"})

        response = fix_client.post(
            "/login",
            data={"username": "new", "password": "pwd12345"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "/"

    @pytest.mark.parametrize(
        ("username", "password"),
        [
            ("non_existent", "password"),
            ("testuser", "wrong_password"),
        ],
    )
    def test_login_failures(
        self, fix_auth_client: FlaskClient, username: str, password: str
    ) -> None:
        """Attempt to login with invalid credentials and expect an error.

        What: POST `/login` using either a non-existent username or a
        wrong password for an existing user.
        Why: Verifies the app properly reports authentication failures
        without redirecting (returns a 200 and shows an error in the
        login template), protecting routes from unauthorized access.
        """
        response = fix_auth_client.post(
            "/login",
            data={"username": username, "password": password},
        )

        assert response.status_code == 200
        assert b"Invalid" in response.data or b"User not found" in response.data
