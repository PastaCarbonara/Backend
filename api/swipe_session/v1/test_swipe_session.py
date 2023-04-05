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


@pytest.mark.asyncio
async def test_swipe_session(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[1]

    admin = users[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('hashed_id')}"
    )

    normal_user = users[1]
    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{normal_user.get('hashed_id')}"
    )

    valid_connection = {
        "action": ssae.CONNECTION_CODE,
        "payload": {"status_code": 200, "message": "You have connected"},
    }

    async def send_swipe(ws: WebSocketTestSession, recipe_id: int, like: bool):
        packet = {
            "action": ssae.RECIPE_SWIPE,
            "payload": {"recipe_id": recipe_id, "like": like},
        }
        await ws.send_json(packet)

    async def send_message(ws: WebSocketTestSession, message: str):
        packet = {"action": ssae.SESSION_MESSAGE, "payload": {"message": message}}
        await ws.send_json(packet)

    async def send_status_update(ws: WebSocketTestSession, status: str):
        packet = {"action": ssae.SESSION_STATUS_UPDATE, "payload": {"status": status}}
        await ws.send_json(packet)

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws_admin, connect(normal_user_url) as ws_normal_user:
        ws_admin: WebSocketTestSession
        ws_normal_user: WebSocketTestSession

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1 == valid_connection
        assert data_2 == valid_connection

        await send_swipe(ws_admin, 1, False)
        await send_swipe(ws_normal_user, 1, True)

        await send_swipe(ws_admin, 1, False)
        data_1 = ws_admin.receive_json()

        assert data_1.get("action") == ssae.CONNECTION_CODE
        assert data_1.get("payload").get("status_code") == 409

        await send_swipe(ws_admin, 3, False)
        data_1 = ws_admin.receive_json()

        assert data_1.get("action") == ssae.CONNECTION_CODE
        assert data_1.get("payload").get("status_code") == 404

        # Session message
        await send_message(ws_admin, "Message!")

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_MESSAGE
        assert data_1.get("payload").get("message") == "Message!"

        assert data_2.get("action") == ssae.SESSION_MESSAGE
        assert data_2.get("payload").get("message") == "Message!"

        await send_message(ws_normal_user, "Message!")

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_MESSAGE
        assert data_1.get("payload").get("message") == "Message!"

        assert data_2.get("action") == ssae.SESSION_MESSAGE
        assert data_2.get("payload").get("message") == "Message!"

        # Status update
        await send_status_update(ws_admin, sse.PAUSED)

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_1.get("payload").get("status") == sse.PAUSED

        assert data_2.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_2.get("payload").get("status") == sse.PAUSED

        await send_status_update(ws_normal_user, sse.IN_PROGRESS)

        data_2 = ws_normal_user.receive_json()

        assert data_2.get("action") == ssae.CONNECTION_CODE
        assert data_2.get("payload").get("status_code") == 401

        # Swipe match
        await send_swipe(ws_admin, 2, True)
        await send_swipe(ws_normal_user, 2, True)

        print("???")

        data_2 = ws_normal_user.receive_json()
        print("???")
        data_1 = ws_admin.receive_json()

        print("???")
        assert data_1.get("action") == ssae.RECIPE_MATCH
        assert data_1.get("payload").get("recipe").get("id") == 2

        assert data_2.get("action") == ssae.RECIPE_MATCH
        assert data_2.get("payload").get("recipe").get("id") == 2
