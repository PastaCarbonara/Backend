# pylint: skip-file

import pytest
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_get_images(client: AsyncClient, admin_token_headers: Dict[str, str]):
    admin_token_headers = await admin_token_headers

    response = await client.get("/api/v1/images", headers=admin_token_headers)
    assert response.status_code == 200
    filenames = [image["filename"] for image in response.json()]
    assert filenames == ["image_1", "image_2", "image_3", "image_4"]


@pytest.mark.asyncio
async def get_image(client: AsyncClient):
    res = await client.get("/api/v1/images/fake_image")
    assert res.status_code == 404

    res = await client.get("/api/v1/images/image_1")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_upload_and_delete_image(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers

    response = await client.post(
        "/api/v1/images",
        headers=admin_token_headers,
        files={"images": open("tests/images/testcake.jpg", "rb")},
    )
    assert response.status_code == 200
    response_image_name: str = response.json()[0]["filename"]
    assert response_image_name != "testcake.jpg"
    assert "testcake" not in response_image_name
    assert "webp" == response_image_name.split(".")[-1]

    response = await client.delete(
        f"/api/v1/images/{response_image_name}", headers=admin_token_headers
    )
    assert response.status_code == 204

    response = await client.get("/api/v1/images", headers=admin_token_headers)
    filenames = [image["filename"] for image in response.json()]
    assert response_image_name not in filenames


@pytest.mark.asyncio
async def test_upload_image_valid(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers

    response = await client.post(
        "/api/v1/images",
        headers=admin_token_headers,
        files={"images": open("tests/images/testcake.txt", "rb")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_image_gif(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers

    response = await client.post(
        "/api/v1/images",
        headers=admin_token_headers,
        files={"images": open("tests/images/test_gif.gif", "rb")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_image_too_large(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers

    response = await client.post(
        "/api/v1/images",
        headers=admin_token_headers,
        files={"images": open("tests/images/test_too_large.jpg", "rb")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_image_not_exist(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    admin_token_headers = await admin_token_headers

    response = await client.delete(
        "/api/v1/images/image_1", headers=admin_token_headers
    )
    assert response.status_code == 409

    response = await client.delete(
        "/api/v1/images/image_x", headers=admin_token_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_not_authorized_to_delete_image(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
):
    normal_user_token_headers = await normal_user_token_headers

    response = await client.delete(
        "/api/v1/images/image_1", headers=normal_user_token_headers
    )
    assert response.status_code == 401
