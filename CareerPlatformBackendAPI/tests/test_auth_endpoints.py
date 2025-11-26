from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from src.api.main import app


# PUBLIC_INTERFACE
def test_auth_routes_exist_and_behavior():
    """Validate auth route registration and expected status codes."""
    with TestClient(app) as client:
        # Root health check should be available
        r = client.get("/")
        assert r.status_code == 200

        # Login with empty payload -> 400 (not 404)
        r = client.post("/api/v1/auth/login", json={})
        assert r.status_code == 400

        # Alias path should also be present and not 404
        r = client.post("/api/v1/login", json={})
        assert r.status_code == 400

        # Login with non-existent user -> 401 (not 404)
        r = client.post("/api/v1/auth/login", json={"email": "does-not-exist@example.com"})
        assert r.status_code == 401

        # Register a new user (unique email to avoid conflicts)
        email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        name = "Test User"
        r = client.post("/api/v1/auth/register", json={"email": email, "name": name})
        assert r.status_code == 201, r.text
        user = r.json()
        assert user.get("email") == email

        # Login the newly registered user -> 200 with token
        r = client.post("/api/v1/auth/login", json={"email": email, "password": "ignored"})
        assert r.status_code == 200, r.text
        data = r.json()
        token = data.get("token")
        assert isinstance(token, str) and len(token) > 0

        # Logout using the token -> 204
        r = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 204

        # Alias logout using the token -> 204
        r = client.post("/api/v1/logout", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 204
