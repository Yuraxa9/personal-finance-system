import uuid

from app.models.category import CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    update_category,
)


async def test_create_category(client, auth_headers):
    response = await client.post(
        "/api/v1/categories/",
        json={"name": "Food", "category_type": "expense", "color": "#00FF00", "icon": "food"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Food"
    assert data["category_type"] == "expense"


async def test_get_categories(client, auth_headers, test_category):
    response = await client.get("/api/v1/categories/", headers=auth_headers)
    assert response.status_code == 200
    assert any(c["name"] == "Test Category" for c in response.json())


async def test_get_category(client, auth_headers, test_category):
    response = await client.get(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(test_category.id)


async def test_get_category_not_found(client, auth_headers):
    response = await client.get(f"/api/v1/categories/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


async def test_update_category(client, auth_headers, test_category):
    response = await client.put(
        f"/api/v1/categories/{test_category.id}",
        json={"name": "Updated Cat", "color": "#0000FF"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Cat"
    assert data["color"] == "#0000FF"


async def test_update_category_not_found(client, auth_headers):
    response = await client.put(
        f"/api/v1/categories/{uuid.uuid4()}",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_delete_category(client, auth_headers, test_category):
    response = await client.delete(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
    assert response.status_code == 204


async def test_delete_category_not_found(client, auth_headers):
    response = await client.delete(
        f"/api/v1/categories/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


# --- direct service tests to cover async lines skipped by ASGI transport ---

async def test_svc_get_categories(db, test_user, test_category):
    cats = await get_categories(db, test_user.id)
    assert any(c.id == test_category.id for c in cats)


async def test_svc_get_category_found(db, test_user, test_category):
    cat = await get_category(db, test_category.id, test_user.id)
    assert cat is not None
    assert cat.id == test_category.id


async def test_svc_get_category_not_found(db, test_user):
    cat = await get_category(db, uuid.uuid4(), test_user.id)
    assert cat is None


async def test_svc_create_category(db, test_user):
    data = CategoryCreate(
        name="Svc Cat",
        category_type=CategoryType.income,
        color="#00FF00",
        icon="cash",
    )
    cat = await create_category(db, test_user.id, data)
    assert cat.id is not None
    assert cat.name == "Svc Cat"


async def test_svc_update_category(db, test_user, test_category):
    updated = await update_category(
        db,
        test_category.id,
        test_user.id,
        CategoryUpdate(name="Updated Svc"),
    )
    assert updated is not None
    assert updated.name == "Updated Svc"


async def test_svc_update_category_not_found(db, test_user):
    result = await update_category(
        db, uuid.uuid4(), test_user.id, CategoryUpdate(name="X")
    )
    assert result is None


async def test_svc_delete_category(db, test_user):
    data = CategoryCreate(
        name="Del Cat",
        category_type=CategoryType.expense,
        color="#FF0000",
        icon="trash",
    )
    cat = await create_category(db, test_user.id, data)
    ok = await delete_category(db, cat.id, test_user.id)
    assert ok is True


async def test_svc_delete_category_not_found(db, test_user):
    ok = await delete_category(db, uuid.uuid4(), test_user.id)
    assert ok is False
