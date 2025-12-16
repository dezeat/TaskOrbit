"""Tests for route handlers."""

from flask import Flask

from app.routes import _handle_unauthorized


def test_handle_unauthorized_hx_header(fix_app: Flask) -> None:
    """HX requests receive an HX-Redirect to login."""
    with fix_app.test_request_context("/", headers={"HX-Request": "true"}):
        resp = _handle_unauthorized()
    assert resp.status_code == 200
    assert "HX-Redirect" in resp.headers
    assert resp.headers["HX-Redirect"].endswith("/login")


def test_handle_unauthorized_redirect(fix_app: Flask) -> None:
    """Non-HX requests are redirected to login endpoint."""
    with fix_app.test_request_context("/"):
        resp = _handle_unauthorized()
    assert resp.status_code in (301, 302, 303, 307, 308)
    assert resp.headers.get("Location", "").endswith("/login")
