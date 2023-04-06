from typing import Dict
from fastapi import Response
from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_get_all_groups_unauthorized(client: AsyncClient):
    response: Response = await client.get(
        "/api/v1/groups",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_groups_authorized(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    res = await client.get("/api/v1/groups", headers=await admin_token_headers)
    groups = res.json()

    assert res.status_code == 200
    assert len(groups) == 3

    assert groups[0].get("name") == "group_1"
    assert len(groups[0].get("users")) == 1

    assert groups[1].get("name") == "group_2"
    assert len(groups[1].get("users")) == 2

    assert groups[2].get("name") == "group_3"
    assert len(groups[2].get("users")) == 1


@pytest.fixture()
async def groups(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> list[Dict[str, str]]:
    res = await client.get("/api/v1/groups", headers=await admin_token_headers)
    return res.json()


@pytest.mark.asyncio
async def test_join_group(
    client: AsyncClient,
    groups: list[Dict[str, str]],
    normal_user_token_headers: Dict[str, str],
):
    groups = await groups

    res = await client.get(
        f"/api/v1/groups/join/{groups[2].get('id')}",
        headers=await normal_user_token_headers,
    )
    json_res = res.json()

    assert res.status_code == 200
    assert json_res is None


@pytest.mark.asyncio
async def test_check_joined(
    groups: list[Dict[str, str]],
):
    groups = await groups

    assert groups[0].get("name") == "group_1"
    assert len(groups[0].get("users")) == 1

    assert groups[1].get("name") == "group_2"
    assert len(groups[1].get("users")) == 2

    assert groups[2].get("name") == "group_3"
    assert len(groups[2].get("users")) == 2


@pytest.mark.asyncio
async def test_already_join_group(
    client: AsyncClient,
    groups: list[Dict[str, str]],
    normal_user_token_headers: Dict[str, str],
    admin_token_headers: Dict[str, str],
):
    groups = await groups

    res = await client.get(
        f"/api/v1/groups/join/{groups[2].get('id')}",
        headers=await normal_user_token_headers,
    )
    json_res = res.json()

    assert res.status_code == 200
    assert json_res is None


@pytest.mark.asyncio
async def test_check_not_joined(
    groups: list[Dict[str, str]],
):
    # previous join attempt should not have let the user in
    # for a second entry
    groups = await groups

    assert groups[0].get("name") == "group_1"
    assert len(groups[0].get("users")) == 1

    assert groups[1].get("name") == "group_2"
    assert len(groups[1].get("users")) == 2

    assert groups[2].get("name") == "group_3"
    assert len(groups[2].get("users")) == 2


@pytest.mark.asyncio
async def test_create_group(
    client: AsyncClient,
    normal_user_token_headers: Dict[str, str],
):
    payload = {"name": "group_4"}
    res = await client.post(
        "/api/v1/groups", json=payload, headers=await normal_user_token_headers
    )

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_create_group(
    client: AsyncClient,
    admin_token_headers: Dict[str, str],
):
    payload = {"name": "group_4"}
    res = await client.post(
        "/api/v1/groups", json=payload, headers=await admin_token_headers
    )
    group = res.json()

    assert res.status_code == 200
    assert group.get("name") == "group_4"
    assert len(group.get("users")) == 1
    assert group.get("users")[0].get("username") == "admin"


@pytest.mark.asyncio
async def test_get_group_unauthorized_not_part_of_group(
    groups: list[Dict[str, str]],
    client: AsyncClient,
    normal_user_token_headers: Dict[str, str],
):
    groups = await groups
    res = await client.get(
        f"/api/v1/groups/{groups[0].get('id')}", headers=await normal_user_token_headers
    )

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_group_authorized_part_of_group(
    groups: list[Dict[str, str]],
    client: AsyncClient,
    normal_user_token_headers: Dict[str, str],
):
    groups = await groups
    res = await client.get(
        f"/api/v1/groups/{groups[1].get('id')}", headers=await normal_user_token_headers
    )

    assert res.status_code == 200
