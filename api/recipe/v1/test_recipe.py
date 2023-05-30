# pylint: skip-file

import pytest
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_get_recipe_list(client: AsyncClient):
    """Test that the recipe list endpoint returns a list of recipes"""
    response = await client.get("/api/v1/recipes")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_recipe_by_id(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    """Test that the recipe by id endpoint returns a recipe"""
    response = await client.get("/api/v1/recipes/1", headers=await admin_token_headers)
    assert response.status_code == 200
    assert response.json().get("id") == 1
    assert response.json().get("name") == "Union pie"


@pytest.mark.asyncio
async def test_judge_recipe(client: AsyncClient, admin_token_headers: Dict[str, str]):
    """Test that the judge recipe endpoint returns a recipe"""
    admin_token_headers = await admin_token_headers
    response = await client.post(
        "/api/v1/recipes/1/judge",
        json={"like": True},
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    response = await client.get("/api/v1/recipes/1", headers=admin_token_headers)
    assert response.json().get("likes") == 1


@pytest.mark.asyncio
async def test_create_recipe(client: AsyncClient, admin_token_headers: Dict[str, str]):
    """Test that the create recipe endpoint returns a recipe"""
    response = await client.post(
        "/api/v1/recipes",
        json={
            "name": "test",
            "filename": "image_1",
            "description": "test",
            "ingredients": [{"name": "test", "amount": 1, "unit": "test"}],
            "instructions": ["test"],
            "tags": [{"name": "dogshit", "tag_type": "Keuken"}],
            "preparation_time": 30,
            "spiciness": 0,
        },
        headers=await admin_token_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_recipe(client: AsyncClient, admin_token_headers: Dict[str, str]):
    """Test that the delete recipe endpoint returns a recipe"""
    response = await client.delete(
        "/api/v1/recipes/3", headers=await admin_token_headers
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_recipe_unauthorized(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
):
    """Test that the delete recipe endpoint returns a recipe"""
    response = await client.delete(
        "/api/v1/recipes/2", headers=await normal_user_token_headers
    )
    assert response.status_code == 401
