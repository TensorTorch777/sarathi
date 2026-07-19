"""Unit/smoke tests for the version endpoint."""

from fastapi.testclient import TestClient


def test_version_endpoint(client: TestClient) -> None:
    """Version endpoint should return application metadata."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"]
    assert payload["version"]
    assert payload["api"] == "v1"
