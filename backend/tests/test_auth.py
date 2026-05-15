import pytest

from app.models.user import User
from app.services.auth import hash_password


async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "pass123", "full_name": "New User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data


async def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "pass123", "full_name": "User"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


async def test_login_success(client, test_user):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client, test_user):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "test@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


async def test_login_inactive_user(client, db):
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("pass123"),
        full_name="Inactive",
        is_active=False,
    )
    db.add(user)
    await db.commit()

    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "inactive@example.com", "password": "pass123"},
    )
    assert response.status_code == 400


async def test_get_me_authorized(client, test_user, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


async def test_get_me_unauthorized(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_get_me_invalid_token(client):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.value"}
    )
    assert response.status_code == 401


async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
