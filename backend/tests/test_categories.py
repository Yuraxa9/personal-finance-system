import uuid


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
    response = await client.delete(f"/api/v1/categories/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
