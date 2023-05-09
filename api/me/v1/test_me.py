# pylint: skip-file

import pytest
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_me(
    normal_user_token_headers: Dict[str, str],
    client: AsyncClient,
):
    res = await client.get("/api/v1/me", headers=await normal_user_token_headers)

    assert res.status_code == 200


@pytest.mark.asyncio
async def test_me_groups(
    normal_user_token_headers: Dict[str, str],
    client: AsyncClient,
):
    res = await client.get("/api/v1/me/groups", headers=await normal_user_token_headers)

    assert res.status_code == 200
