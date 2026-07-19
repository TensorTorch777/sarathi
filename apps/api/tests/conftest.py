"""Shared pytest fixtures for the API skeleton."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous TestClient for smoke tests."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
