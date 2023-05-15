# pylint: skip-file

import pytest
from typing import Dict
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_tags(client: AsyncClient, admin_token_headers: Dict[str, str]):
    response = await client.get("/api/v1/tags", headers=await admin_token_headers)
    assert response.status_code == 200
    expected_tags = ["tag1", "tag2", "tag3"]
    tags = [tag["name"] for tag in response.json()]
    for expected_tag in expected_tags:
        assert expected_tag in tags


@pytest.mark.asyncio
async def test_delete_tag(client: AsyncClient, admin_token_headers: Dict[str, str]):
    admin_token_headers = await admin_token_headers
    response = await client.delete("/api/v1/tags/1", headers=admin_token_headers)
    assert response.status_code == 204
    response = await client.get("/api/v1/tags", headers=admin_token_headers)
    tags = [tag["id"] for tag in response.json()]
    assert 1 not in tags


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
        json={"name": "tag4", "tag_type":"Keuken"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "tag4"
    response = await client.get("/api/v1/tags", headers=admin_token_headers)
    expected_tags = ["tag2", "tag3", "tag4"]
    tags = [tag["name"] for tag in response.json()]
    for expected_tag in expected_tags:
        assert expected_tag in tags


@pytest.mark.asyncio
async def test_create_tag_already_exists(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.post(
        "/api/v1/tags",
        headers=admin_token_headers,
        json={"name": "tag4", "tag_type":"Keuken"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_tag(client: AsyncClient, admin_token_headers: Dict[str, str]):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/tags/2",
        headers=admin_token_headers,
        json={"name": "tag5", "tag_type":"Keuken"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "tag5", "tag_type":"Keuken"}
    response = await client.get("/api/v1/tags", headers=admin_token_headers)
    expected_tags = ["tag3", "tag4", "tag5"]
    tags = [tag["name"] for tag in response.json()]
    for expected_tag in expected_tags:
        assert expected_tag in tags


@pytest.mark.asyncio
async def test_update_tag_already_exists(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/tags/2",
        headers=admin_token_headers,
        json={"name": "tag4", "tag_type":"Keuken"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_tag_not_found(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers
    response = await client.put(
        "/api/v1/tags/9",
        headers=admin_token_headers,
        json={"name": "tag5", "tag_type":"Keuken"},
    )
    assert response.status_code == 404
