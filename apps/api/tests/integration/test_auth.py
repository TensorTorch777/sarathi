"""Integration tests for JWT authentication flows."""

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """API client with lifespan (DB + Redis)."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}@example.com"


def test_register_login_me_logout_refresh(client: TestClient) -> None:
    """Happy-path auth lifecycle."""
    email = _email("seeker")
    password = "securepass123"

    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "display_name": "Seeker"},
    )
    assert register.status_code == 201, register.text
    body = register.json()
    assert body["user"]["email"] == email
    assert body["user"]["role"] == "user"
    assert body["tokens"]["access_token"]
    assert body["tokens"]["refresh_token"]

    access = body["tokens"]["access_token"]

    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == email

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    login_refresh = login.json()["tokens"]["refresh_token"]

    rotated = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_refresh},
    )
    assert rotated.status_code == 200
    new_access = rotated.json()["access_token"]
    new_refresh = rotated.json()["refresh_token"]

    # Old refresh should no longer work after rotation.
    stale = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_refresh},
    )
    assert stale.status_code == 401

    logout = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_access}"},
        json={"refresh_token": new_refresh},
    )
    assert logout.status_code == 200

    denied = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert denied.status_code == 401


def test_duplicate_register_conflict(client: TestClient) -> None:
    """Registering the same email twice returns 409."""
    payload = {"email": _email("dup"), "password": "securepass123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    again = client.post("/api/v1/auth/register", json=payload)
    assert again.status_code == 409


def test_admin_ping_forbidden_for_user(client: TestClient) -> None:
    """Regular users cannot access admin-only routes."""
    register = client.post(
        "/api/v1/auth/register",
        json={"email": _email("member"), "password": "securepass123"},
    )
    access = register.json()["tokens"]["access_token"]
    response = client.get(
        "/api/v1/users/admin/ping",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 403


def test_password_reset_placeholder(client: TestClient) -> None:
    """Password reset placeholder returns a neutral acknowledgement."""
    response = client.post(
        "/api/v1/auth/password-reset",
        json={"email": "anyone@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_oauth_placeholder(client: TestClient) -> None:
    """OAuth endpoints are reserved and return 501."""
    response = client.get("/api/v1/auth/oauth/google/authorize")
    assert response.status_code == 501
