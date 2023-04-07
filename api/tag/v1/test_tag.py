"""Tests for the tag endpoints"""
import pytest
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_get_tags(client: AsyncClient, admin_token_headers: Dict[str, str]):
    response = await client.get("/api/v1/tags", headers=await admin_token_headers)
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "tag1"},
        {"id": 2, "name": "tag2"},
        {"id": 3, "name": "tag3"},
    ]


@pytest.mark.asyncio
async def test_delete_tag(client: AsyncClient, admin_token_headers: Dict[str, str]):
    admin_token_headers = await admin_token_headers
    response = await client.delete("/api/v1/tags/1", headers=admin_token_headers)
    assert response.status_code == 204
    response = await client.get("/api/v1/tags", headers=admin_token_headers)
    assert response.json() == [
        {"id": 2, "name": "tag2"},
        {"id": 3, "name": "tag3"},
    ]


@pytest.mark.asyncio
async def test_delete_tag_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.delete("/api/v1/tags/1", headers=admin_token_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient, admin_token_headers: Dict[str, str]):
    admin_token_headers = await admin_token_headers
    response = await client.post(
        "/api/v1/tags",
        headers=admin_token_headers,
        json={"name": "tag4"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 4, "name": "tag4"}
    response = await client.get("/api/v1/tags", headers=admin_token_headers)
    assert response.json() == [
        {"id": 2, "name": "tag2"},
        {"id": 3, "name": "tag3"},
        {"id": 4, "name": "tag4"},
    ]


@pytest.mark.asyncio
async def test_create_tag_already_exists(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.post(
        "/api/v1/tags",
        headers=admin_token_headers,
        json={"name": "tag4"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_tag(client: AsyncClient, admin_token_headers: Dict[str, str]):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/tags/2",
        headers=admin_token_headers,
        json={"name": "tag5"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "tag5"}
    response = await client.get("/api/v1/tags", headers=admin_token_headers)
    assert response.json() == [
        {"id": 2, "name": "tag5"},
        {"id": 3, "name": "tag3"},
        {"id": 4, "name": "tag4"},
    ]


@pytest.mark.asyncio
async def test_update_tag_already_exists(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/tags/2",
        headers=admin_token_headers,
        json={"name": "tag4"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_tag_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/tags/5",
        headers=admin_token_headers,
        json={"name": "tag5"},
    )
    assert response.status_code == 404
