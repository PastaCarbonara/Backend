from fastapi import Response
import pytest
import pytest
from app.server import app
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response: Response = await client.post(
        "/api/v1/users",
        json={"username": "admin1", "password": "admin1"},
    )
    print("porn")
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
    res = await client.get("/api/latest/users", headers=await admin_token_headers)
    users = res.json()

    assert users[0]["username"] == "admin"
    assert users[1]["username"] == "admin1"
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_user_list_no_auth(client: AsyncClient):
    res = await client.get("/api/latest/users")
    assert res.status_code == 401
