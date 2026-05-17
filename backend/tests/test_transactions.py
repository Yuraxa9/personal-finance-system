import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.transaction import TransactionType
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionUpdate
from app.services.transaction import (
    create_transaction,
    delete_transaction,
    get_analytics,
    get_transaction,
    get_transactions,
    update_transaction,
)


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
    r = await client.delete(
        f"/api/v1/transactions/{uuid.uuid4()}", headers=auth_headers
    )
    assert r.status_code == 404


async def test_create_transaction_zero_amount(client, auth_headers, test_account):
    response = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "0.00",
            "transaction_type": "income",
            "date": "2024-01-15T12:00:00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_create_transaction_negative_amount(
    client, auth_headers, test_account
):
    response = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "-50.00",
            "transaction_type": "income",
            "date": "2024-01-15T12:00:00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_create_transaction_future_date(client, auth_headers, test_account):
    future = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    response = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "100.00",
            "transaction_type": "income",
            "date": future,
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_create_transaction_invalid_category(
    client, auth_headers, test_account
):
    response = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "100.00",
            "transaction_type": "expense",
            "date": "2024-01-15T12:00:00",
            "category_id": str(uuid.uuid4()),
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


async def test_update_transaction_zero_amount(client, auth_headers, test_account):
    create_r = await _create_tx(
        client, auth_headers, test_account.id, INCOME_PAYLOAD
    )
    tx_id = create_r.json()["id"]
    r = await client.put(
        f"/api/v1/transactions/{tx_id}",
        json={"amount": "0.00"},
        headers=auth_headers,
    )
    assert r.status_code == 422


async def test_update_transaction_future_date(client, auth_headers, test_account):
    create_r = await _create_tx(
        client, auth_headers, test_account.id, INCOME_PAYLOAD
    )
    tx_id = create_r.json()["id"]
    future = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    r = await client.put(
        f"/api/v1/transactions/{tx_id}",
        json={"date": future},
        headers=auth_headers,
    )
    assert r.status_code == 422


async def test_update_transaction_invalid_category(
    client, auth_headers, test_account
):
    create_r = await _create_tx(
        client, auth_headers, test_account.id, INCOME_PAYLOAD
    )
    tx_id = create_r.json()["id"]
    r = await client.put(
        f"/api/v1/transactions/{tx_id}",
        json={"category_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert r.status_code == 403


async def test_get_transactions_with_category_filter(
    client, auth_headers, test_account, test_category
):
    await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "100.00",
            "transaction_type": "expense",
            "date": "2024-01-15T12:00:00",
            "category_id": str(test_category.id),
        },
        headers=auth_headers,
    )
    r = await client.get(
        "/api/v1/transactions/",
        params={"category_id": str(test_category.id)},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_analytics_with_transfer(client, auth_headers, test_account):
    await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": "100.00",
            "transaction_type": "transfer",
            "date": "2024-01-15T12:00:00",
        },
        headers=auth_headers,
    )
    r = await client.get("/api/v1/transactions/analytics", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert float(data["summary"]["balance"]) == -100.0


# --- direct service tests to cover async lines skipped by ASGI transport ---

_TX_DATE = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def _income_data(account_id, amount="100.00"):
    return TransactionCreate(
        account_id=account_id,
        amount=Decimal(amount),
        transaction_type=TransactionType.income,
        date=_TX_DATE,
    )


def _expense_data(account_id, amount="50.00"):
    return TransactionCreate(
        account_id=account_id,
        amount=Decimal(amount),
        transaction_type=TransactionType.expense,
        date=_TX_DATE,
    )


async def test_svc_create_and_get_transaction(db, test_user, test_account):
    tx = await create_transaction(db, test_user.id, _income_data(test_account.id))
    assert tx.id is not None
    found = await get_transaction(db, tx.id, test_user.id)
    assert found is not None
    assert found.id == tx.id


async def test_svc_get_transaction_not_found(db, test_user):
    result = await get_transaction(db, uuid.uuid4(), test_user.id)
    assert result is None


async def test_svc_get_transactions_filters(db, test_user, test_account):
    await create_transaction(db, test_user.id, _income_data(test_account.id))
    await create_transaction(db, test_user.id, _expense_data(test_account.id))

    all_txs = await get_transactions(db, test_user.id, TransactionFilter())
    assert len(all_txs) == 2

    income_only = await get_transactions(
        db,
        test_user.id,
        TransactionFilter(transaction_type=TransactionType.income),
    )
    assert len(income_only) == 1

    by_account = await get_transactions(
        db,
        test_user.id,
        TransactionFilter(account_id=test_account.id),
    )
    assert len(by_account) == 2

    date_filtered = await get_transactions(
        db,
        test_user.id,
        TransactionFilter(
            date_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
            date_to=datetime(2024, 12, 31, tzinfo=timezone.utc),
        ),
    )
    assert len(date_filtered) == 2


async def test_svc_update_transaction(db, test_user, test_account):
    tx = await create_transaction(db, test_user.id, _expense_data(test_account.id))
    updated = await update_transaction(
        db, tx.id, test_user.id, TransactionUpdate(amount=Decimal("75.00"))
    )
    assert updated is not None
    assert updated.amount == Decimal("75.00")


async def test_svc_update_transaction_not_found(db, test_user):
    result = await update_transaction(
        db, uuid.uuid4(), test_user.id, TransactionUpdate(description="x")
    )
    assert result is None


async def test_svc_delete_transaction(db, test_user, test_account):
    tx = await create_transaction(db, test_user.id, _income_data(test_account.id))
    ok = await delete_transaction(db, tx.id, test_user.id)
    assert ok is True


async def test_svc_delete_transaction_not_found(db, test_user):
    ok = await delete_transaction(db, uuid.uuid4(), test_user.id)
    assert ok is False


async def test_svc_get_analytics(db, test_user, test_account):
    await create_transaction(
        db,
        test_user.id,
        TransactionCreate(
            account_id=test_account.id,
            amount=Decimal("200.00"),
            transaction_type=TransactionType.income,
            date=_TX_DATE,
        ),
    )
    await create_transaction(
        db,
        test_user.id,
        TransactionCreate(
            account_id=test_account.id,
            amount=Decimal("80.00"),
            transaction_type=TransactionType.expense,
            date=_TX_DATE,
        ),
    )
    await create_transaction(
        db,
        test_user.id,
        TransactionCreate(
            account_id=test_account.id,
            amount=Decimal("50.00"),
            transaction_type=TransactionType.transfer,
            date=_TX_DATE,
        ),
    )

    result = await get_analytics(db, test_user.id, None, None)
    assert result.summary.total_income == Decimal("200.00")
    assert result.summary.total_expense == Decimal("80.00")

    result_dated = await get_analytics(
        db,
        test_user.id,
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 12, 31, tzinfo=timezone.utc),
    )
    assert result_dated.summary.total_income == Decimal("200.00")
