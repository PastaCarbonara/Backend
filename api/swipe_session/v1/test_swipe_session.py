from typing import Dict
from fastapi import Response
from httpx import AsyncClient
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
import pytest

from core.db.enums import SwipeSessionEnum as sse
from core.db.enums import SwipeSessionActionEnum as ssae


@pytest.fixture()
async def sessions(
    client: AsyncClient, admin_token_headers: Dict[str, str]
) -> list[Dict[str, str]]:
    res = await client.get("/api/v1/swipe_sessions", headers=await admin_token_headers)
    return res.json()


@pytest.mark.asyncio
async def test_action_docs(client: AsyncClient):
    res = await client.get("/api/v1/swipe_sessions/actions_docs")
    docs = res.json()

    assert res.status_code == 200
    assert type(docs) == dict
    assert [action for action in docs.get("actions")] == [action for action in ssae]


@pytest.mark.asyncio
async def test_get_sessions_unautherized(
    client: AsyncClient,
):
    response: Response = await client.get(
        "/api/v1/swipe_sessions",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_sessions_authorized(
    client: AsyncClient, admin_token_headers: Dict[str, str]
):
    res = await client.get("/api/v1/swipe_sessions", headers=await admin_token_headers)
    sessions = res.json()

    assert res.status_code == 200
    assert len(sessions) == 3
    assert not any([i.get("status") != sse.READY for i in sessions])


@pytest.mark.asyncio
async def test_update_session(
    admin_token_headers: Dict[str, str],
    fastapi_client: TestClient,
):
    headers = await admin_token_headers

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    payload = {"id": sessions[0].get("id"), "status": sse.IN_PROGRESS}

    res = fastapi_client.patch("/api/v1/swipe_sessions", json=payload, headers=headers)
    swipe_session = res.json()

    assert res.status_code == 200
    assert swipe_session.get("status") != sessions[0].get("status")
    assert swipe_session.get("status") == sse.IN_PROGRESS


@pytest.mark.asyncio
async def test_websocket_invalid_id(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    assert users[0].get("hashed_id") is not None, "THE USER DTO MIGHT HAVE CHANGED!!!!"

    invalid_id_response = {
        "action": ssae.CONNECTION_CODE,
        "payload": {"status_code": 400, "message": "Invalid ID"},
    }

    valid_connection = {
        "action": ssae.CONNECTION_CODE,
        "payload": {"status_code": 200, "message": "You have connected"},
    }

    with fastapi_client.websocket_connect("/api/v1/swipe_sessions/1/1") as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert data == invalid_id_response

    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/{sessions[0].get('id')}/1"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert data == invalid_id_response

    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/1/{users[0].get('hashed_id')}"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert data == invalid_id_response

    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/{sessions[0].get('id')}/{users[0].get('hashed_id')}"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert data == valid_connection
