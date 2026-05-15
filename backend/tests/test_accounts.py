import uuid


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
    response = await client.delete(f"/api/v1/accounts/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
