import uuid

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth import (
    authenticate_user,
    change_user_password,
    create_access_token,
    create_user,
    get_user_by_email,
    hash_password,
    update_user_profile,
)


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


async def test_update_me(client, test_user, auth_headers):
    response = await client.patch(
        "/api/v1/auth/me",
        json={"full_name": "Updated Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


async def test_change_password_success(client, test_user, auth_headers):
    response = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "testpassword", "new_password": "newpass123"},
        headers=auth_headers,
    )
    assert response.status_code == 204


async def test_change_password_wrong_current(client, test_user, auth_headers):
    response = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrongpass", "new_password": "newpass123"},
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_get_current_user_no_sub(client):
    token = create_access_token({})
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


async def test_get_current_user_user_not_found(client):
    token = create_access_token({"sub": str(uuid.uuid4())})
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


async def test_get_db_yields_session():
    from unittest.mock import AsyncMock, patch
    from app.dependencies import get_db

    mock_session = AsyncMock()

    class _FakeCtx:
        async def __aenter__(self):
            return mock_session

        async def __aexit__(self, *args):
            return None

    with patch("app.dependencies.AsyncSessionLocal", return_value=_FakeCtx()):
        gen = get_db()
        session = await gen.__anext__()
        assert session is mock_session
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass


async def test_get_stats_empty(client, auth_headers):
    r = await client.get("/api/v1/stats", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_accounts"] == 0
    assert data["total_transactions"] == 0
    assert data["total_income"] == "0.00"
    assert data["total_expense"] == "0.00"


async def test_get_stats_with_data(client, auth_headers, test_account):
    await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "500.00",
            "transaction_type": "income",
            "date": "2024-01-15T12:00:00",
        },
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "200.00",
            "transaction_type": "expense",
            "date": "2024-01-15T12:00:00",
        },
        headers=auth_headers,
    )
    r = await client.get("/api/v1/stats", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total_accounts"] >= 1
    assert data["total_transactions"] >= 2
    assert float(data["total_income"]) == 500.0
    assert float(data["total_expense"]) == 200.0


# --- direct service tests to cover async lines skipped by ASGI transport ---

async def test_svc_get_user_by_email_found(db, test_user):
    user = await get_user_by_email(db, test_user.email)
    assert user is not None
    assert user.id == test_user.id


async def test_svc_get_user_by_email_not_found(db):
    user = await get_user_by_email(db, "nobody@example.com")
    assert user is None


async def test_svc_create_user(db):
    user = await create_user(
        db,
        UserCreate(
            email="svc@example.com",
            password="pass123",
            full_name="Svc User",
        ),
    )
    assert user.id is not None
    assert user.email == "svc@example.com"


async def test_svc_authenticate_user_success(db, test_user):
    user = await authenticate_user(db, test_user.email, "testpassword")
    assert user is not None
    assert user.id == test_user.id


async def test_svc_authenticate_user_wrong_password(db, test_user):
    user = await authenticate_user(db, test_user.email, "wrong")
    assert user is None


async def test_svc_authenticate_user_not_found(db):
    user = await authenticate_user(db, "ghost@example.com", "pass")
    assert user is None


async def test_svc_update_user_profile(db, test_user):
    updated = await update_user_profile(db, test_user, "New Name")
    assert updated.full_name == "New Name"


async def test_svc_change_password_success(db, test_user):
    ok = await change_user_password(db, test_user, "testpassword", "new123")
    assert ok is True


async def test_svc_change_password_wrong(db, test_user):
    ok = await change_user_password(db, test_user, "badpass", "new123")
    assert ok is False
