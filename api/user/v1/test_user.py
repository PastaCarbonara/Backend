from fastapi import Response
import pytest
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response: Response = await client.post(
        "/api/v1/users",
        json={"username": "user3", "password": "user3"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_existing_user(client: AsyncClient):
    # response should be 400 since admin exists
    response: Response = await client.post(
        "/api/v1/users",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_user_list(client: AsyncClient, admin_token_headers: Dict[str, str]):
    res = await client.get("/api/v1/users", headers=await admin_token_headers)
    users = res.json()

    assert users[0]["username"] == "admin"
    assert users[1]["username"] == "normal_user"
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_user_list_normal_user(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
):
    res = await client.get("/api/v1/users", headers=await normal_user_token_headers)
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_user_list_no_auth(client: AsyncClient):
    res = await client.get("/api/v1/users")
    assert res.status_code == 401
