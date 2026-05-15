import uuid


INCOME_PAYLOAD = {
    "amount": "500.00",
    "transaction_type": "income",
    "date": "2024-01-15T12:00:00",
}

EXPENSE_PAYLOAD = {
    "amount": "300.00",
    "transaction_type": "expense",
    "date": "2024-01-15T12:00:00",
}


async def _create_tx(client, headers, account_id, payload):
    return await client.post(
        "/api/v1/transactions/",
        json={"account_id": str(account_id), **payload},
        headers=headers,
    )


async def _get_balance(client, headers, account_id):
    r = await client.get(f"/api/v1/accounts/{account_id}", headers=headers)
    return float(r.json()["balance"])


async def test_create_income(client, auth_headers, test_account):
    response = await _create_tx(client, auth_headers, test_account.id, INCOME_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["transaction_type"] == "income"
    assert await _get_balance(client, auth_headers, test_account.id) == 1500.0


async def test_create_expense(client, auth_headers, test_account):
    response = await _create_tx(client, auth_headers, test_account.id, EXPENSE_PAYLOAD)
    assert response.status_code == 201
    assert await _get_balance(client, auth_headers, test_account.id) == 700.0


async def test_create_transaction_account_not_found(client, auth_headers):
    response = await client.post(
        "/api/v1/transactions/",
        json={"account_id": str(uuid.uuid4()), **INCOME_PAYLOAD},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_get_transactions(client, auth_headers, test_account):
    await _create_tx(client, auth_headers, test_account.id, INCOME_PAYLOAD)

    # no filter
    r = await client.get("/api/v1/transactions/", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    # filter by account
    r = await client.get(
        "/api/v1/transactions/",
        params={"account_id": str(test_account.id)},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert len(r.json()) == 1

    # filter by type
    r = await client.get(
        "/api/v1/transactions/",
        params={"transaction_type": "income"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert len(r.json()) == 1

    # filter by date range
    r = await client.get(
        "/api/v1/transactions/",
        params={"date_from": "2024-01-01T00:00:00", "date_to": "2024-12-31T23:59:59"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert len(r.json()) == 1

    # filter that misses
    r = await client.get(
        "/api/v1/transactions/",
        params={"transaction_type": "expense"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert len(r.json()) == 0


async def test_get_analytics(client, auth_headers, test_account):
    await _create_tx(client, auth_headers, test_account.id, {**INCOME_PAYLOAD, "amount": "1000.00"})
    await _create_tx(client, auth_headers, test_account.id, {**EXPENSE_PAYLOAD, "amount": "400.00"})

    r = await client.get(
        "/api/v1/transactions/analytics",
        params={"date_from": "2024-01-01T00:00:00", "date_to": "2024-12-31T23:59:59"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert float(data["summary"]["total_income"]) == 1000.0
    assert float(data["summary"]["total_expense"]) == 400.0
    assert float(data["summary"]["balance"]) == 600.0
    assert len(data["by_category"]) >= 1


async def test_get_analytics_no_dates(client, auth_headers, test_account):
    r = await client.get("/api/v1/transactions/analytics", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["period"]["date_from"] is None
    assert data["period"]["date_to"] is None


async def test_get_transaction(client, auth_headers, test_account):
    create_r = await _create_tx(client, auth_headers, test_account.id, INCOME_PAYLOAD)
    tx_id = create_r.json()["id"]

    r = await client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == tx_id


async def test_get_transaction_not_found(client, auth_headers):
    r = await client.get(f"/api/v1/transactions/{uuid.uuid4()}", headers=auth_headers)
    assert r.status_code == 404


async def test_update_transaction_amount(client, auth_headers, test_account):
    create_r = await _create_tx(client, auth_headers, test_account.id, {**EXPENSE_PAYLOAD, "amount": "200.00"})
    tx_id = create_r.json()["id"]
    # balance after expense: 1000 - 200 = 800

    r = await client.put(
        f"/api/v1/transactions/{tx_id}",
        json={"amount": "150.00"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert float(r.json()["amount"]) == 150.0
    # revert 200, apply 150: 1000 - 150 = 850
    assert await _get_balance(client, auth_headers, test_account.id) == 850.0


async def test_update_transaction_description_only(client, auth_headers, test_account):
    create_r = await _create_tx(client, auth_headers, test_account.id, EXPENSE_PAYLOAD)
    tx_id = create_r.json()["id"]

    r = await client.put(
        f"/api/v1/transactions/{tx_id}",
        json={"description": "updated desc"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["description"] == "updated desc"
    # balance unchanged
    assert await _get_balance(client, auth_headers, test_account.id) == 700.0


async def test_update_transaction_not_found(client, auth_headers):
    r = await client.put(
        f"/api/v1/transactions/{uuid.uuid4()}",
        json={"description": "x"},
        headers=auth_headers,
    )
    assert r.status_code == 404


async def test_delete_transaction(client, auth_headers, test_account):
    create_r = await _create_tx(client, auth_headers, test_account.id, {**EXPENSE_PAYLOAD, "amount": "300.00"})
    tx_id = create_r.json()["id"]
    assert await _get_balance(client, auth_headers, test_account.id) == 700.0

    r = await client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert r.status_code == 204
    assert await _get_balance(client, auth_headers, test_account.id) == 1000.0


async def test_delete_transaction_not_found(client, auth_headers):
    r = await client.delete(f"/api/v1/transactions/{uuid.uuid4()}", headers=auth_headers)
    assert r.status_code == 404
