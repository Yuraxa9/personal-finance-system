import uuid
from decimal import Decimal

from app.models.account import AccountType
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.account import (
    create_account,
    delete_account,
    get_account,
    get_accounts,
    update_account,
)


async def test_create_account(client, auth_headers):
    response = await client.post(
        "/api/v1/accounts/",
        json={"name": "My Wallet", "account_type": "cash", "balance": "500.00", "currency": "RUB"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Wallet"
    assert data["account_type"] == "cash"
    assert float(data["balance"]) == 500.0


async def test_get_accounts(client, auth_headers, test_account):
    response = await client.get("/api/v1/accounts/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(a["name"] == "Test Account" for a in data)


async def test_get_account(client, auth_headers, test_account):
    response = await client.get(f"/api/v1/accounts/{test_account.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(test_account.id)


async def test_get_account_not_found(client, auth_headers):
    response = await client.get(f"/api/v1/accounts/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


async def test_update_account(client, auth_headers, test_account):
    response = await client.put(
        f"/api/v1/accounts/{test_account.id}",
        json={"name": "Updated", "is_active": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["is_active"] is False


async def test_update_account_not_found(client, auth_headers):
    response = await client.put(
        f"/api/v1/accounts/{uuid.uuid4()}",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_delete_account(client, auth_headers, test_account):
    response = await client.delete(f"/api/v1/accounts/{test_account.id}", headers=auth_headers)
    assert response.status_code == 204


async def test_delete_account_not_found(client, auth_headers):
    response = await client.delete(
        f"/api/v1/accounts/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


async def test_create_account_negative_balance(client, auth_headers):
    response = await client.post(
        "/api/v1/accounts/",
        json={
            "name": "Bad Account",
            "account_type": "cash",
            "balance": "-100.00",
            "currency": "RUB",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_delete_account_with_transactions(client, auth_headers, test_account):
    await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "100.00",
            "transaction_type": "income",
            "date": "2024-01-15T12:00:00",
        },
        headers=auth_headers,
    )
    response = await client.delete(
        f"/api/v1/accounts/{test_account.id}", headers=auth_headers
    )
    assert response.status_code == 422


# --- direct service tests to cover async lines skipped by ASGI transport ---

async def test_svc_get_accounts(db, test_user, test_account):
    result = await get_accounts(db, test_user.id)
    assert any(a.id == test_account.id for a in result)


async def test_svc_get_account_found(db, test_user, test_account):
    account = await get_account(db, test_account.id, test_user.id)
    assert account is not None
    assert account.id == test_account.id


async def test_svc_get_account_not_found(db, test_user):
    account = await get_account(db, uuid.uuid4(), test_user.id)
    assert account is None


async def test_svc_create_account(db, test_user):
    data = AccountCreate(
        name="Svc Acc",
        account_type=AccountType.cash,
        balance=Decimal("0.00"),
        currency="RUB",
    )
    account = await create_account(db, test_user.id, data)
    assert account.id is not None
    assert account.name == "Svc Acc"


async def test_svc_update_account(db, test_user, test_account):
    updated = await update_account(
        db, test_account.id, test_user.id, AccountUpdate(name="Changed")
    )
    assert updated is not None
    assert updated.name == "Changed"


async def test_svc_update_account_not_found(db, test_user):
    result = await update_account(
        db, uuid.uuid4(), test_user.id, AccountUpdate(name="X")
    )
    assert result is None


async def test_svc_delete_account(db, test_user):
    data = AccountCreate(
        name="Del Acc",
        account_type=AccountType.cash,
        balance=Decimal("0.00"),
        currency="RUB",
    )
    account = await create_account(db, test_user.id, data)
    ok = await delete_account(db, account.id, test_user.id)
    assert ok is True


async def test_svc_delete_account_not_found(db, test_user):
    ok = await delete_account(db, uuid.uuid4(), test_user.id)
    assert ok is False
