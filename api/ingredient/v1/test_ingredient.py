# pylint: skip-file

import pytest
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_get_ingredients(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    response = await client.get(
        "/api/v1/ingredients", headers=await admin_token_headers
    )
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "ingredient1"},
        {"id": 2, "name": "ingredient2"},
        {"id": 3, "name": "ingredient3"},
    ]


@pytest.mark.asyncio
async def test_get_ingredient_by_id(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    response = await client.get(
        "/api/v1/ingredients/1", headers=await admin_token_headers
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "ingredient1"}


@pytest.mark.asyncio
async def test_get_ingredient_by_id_not_found(client: AsyncClient):
    response = await client.get("/api/v1/ingredients/9")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_ingredient(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.post(
        "/api/v1/ingredients",
        headers=admin_token_headers,
        json={"name": "ingredient4"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 4, "name": "ingredient4"}
    response = await client.get("/api/v1/ingredients", headers=admin_token_headers)
    assert response.json() == [
        {"id": 1, "name": "ingredient1"},
        {"id": 2, "name": "ingredient2"},
        {"id": 3, "name": "ingredient3"},
        {"id": 4, "name": "ingredient4"},
    ]


@pytest.mark.asyncio
async def test_create_ingredient_already_exists(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.post(
        "/api/v1/ingredients",
        headers=admin_token_headers,
        json={"name": "ingredient1"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_ingredient(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/ingredients/1",
        headers=admin_token_headers,
        json={"name": "ingredient5"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "ingredient5"}
    response = await client.get("/api/v1/ingredients", headers=admin_token_headers)
    assert response.json() == [
        {"id": 1, "name": "ingredient5"},
        {"id": 2, "name": "ingredient2"},
        {"id": 3, "name": "ingredient3"},
        {"id": 4, "name": "ingredient4"},
    ]


@pytest.mark.asyncio
async def test_update_ingredient_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/ingredients/5",
        headers=admin_token_headers,
        json={"name": "ingredient4"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_ingredient_already_exists(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/ingredients/1",
        headers=admin_token_headers,
        json={"name": "ingredient2"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_ingredient(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.delete("/api/v1/ingredients/1", headers=admin_token_headers)
    assert response.status_code == 204
    response = await client.get("/api/v1/ingredients", headers=admin_token_headers)
    assert response.json() == [
        {"id": 2, "name": "ingredient2"},
        {"id": 3, "name": "ingredient3"},
        {"id": 4, "name": "ingredient4"},
    ]


@pytest.mark.asyncio
async def test_delete_ingredient_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.delete("/api/v1/ingredients/5", headers=admin_token_headers)
    assert response.status_code == 404
