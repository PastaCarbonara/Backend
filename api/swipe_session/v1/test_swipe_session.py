import asyncio
import time
from typing import Dict
from fastapi import Response
from httpx import AsyncClient
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
import pytest

from core.db.enums import SwipeSessionEnum as sse
from core.db.enums import SwipeSessionActionEnum as ssae

# Some things I reuse
invalid_id_response = {
    "action": ssae.CONNECTION_CODE,
    "payload": {"status_code": 400, "message": "Invalid ID"},
}

valid_connection = {
    "action": ssae.CONNECTION_CODE,
    "payload": {"status_code": 200, "message": "You have connected"},
}

invalid_json = {
    "action": ssae.CONNECTION_CODE,
    "payload": {"status_code": 400, "message": "Data is not JSON serializable"},
}

invalid_action = {
    "action": ssae.CONNECTION_CODE,
    "payload": {"status_code": 400, "message": "Action does not exist"},
}

invalid_status = {
    "action": ssae.CONNECTION_CODE,
    "payload": {"status_code": 400, "message": "Incorrect status"},
}

invalid_message = {
    "action": ssae.CONNECTION_CODE,
    "payload": {"status_code": 400, "message": "No message provided"},
}


def send_swipe(ws: WebSocketTestSession, recipe_id: int, like: bool):
    packet = {
        "action": ssae.RECIPE_SWIPE,
        "payload": {"recipe_id": recipe_id, "like": like},
    }
    ws.send_json(packet)


def send_message(ws: WebSocketTestSession, message: str):
    packet = {"action": ssae.SESSION_MESSAGE, "payload": {"message": message}}
    ws.send_json(packet)


def send_global_message(ws: WebSocketTestSession, message: str):
    packet = {"action": ssae.GLOBAL_MESSAGE, "payload": {"message": message}}
    ws.send_json(packet)


def send_status_update(ws: WebSocketTestSession, status: str):
    packet = {"action": ssae.SESSION_STATUS_UPDATE, "payload": {"status": status}}
    ws.send_json(packet)


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
async def test_create_session(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    groups = res.json()

    payload = {"group_id": groups[0].get("id")}
    res = fastapi_client.post(
        "/api/v1/swipe_sessions", headers=headers, json=payload
    )
    session = res.json()

    assert res.status_code == 200
    assert session.get("group_id") == groups[0].get("id")
    assert len(session.get("swipes")) == 0


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
async def test_not_in_group(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[0]

    normal_user = users[1]
    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{normal_user.get('hashed_id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(normal_user_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert data == invalid_id_response


@pytest.mark.asyncio
async def test_invalid_json(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[0]

    admin = users[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('hashed_id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert data == valid_connection

        ws.send_text("I am not JSON")
        data = ws.receive_json()

        assert data == invalid_json


@pytest.mark.asyncio
async def test_invalid_action(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[0]

    admin = users[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('hashed_id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert data == valid_connection

        ws.send_json({"action": "BANANA"})
        data = ws.receive_json()

        assert data == invalid_action


@pytest.mark.asyncio
async def test_invalid_status_update(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[0]

    admin = users[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('hashed_id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert data == valid_connection

        send_status_update(ws, "Some status")
        data = ws.receive_json()

        assert data == invalid_status


@pytest.mark.asyncio
async def test_invalid_recipe(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[0]

    admin = users[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('hashed_id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert data == valid_connection

        send_swipe(ws, "haha recipe ID is not an int", True)
        data = ws.receive_json()

        assert data.get("action") == ssae.CONNECTION_CODE
        assert data.get("payload").get("status_code") == 400


@pytest.mark.asyncio
async def test_invalid_message(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[0]

    admin = users[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('hashed_id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert data == valid_connection

        send_message(ws, None)
        data = ws.receive_json()

        assert data == invalid_message

        send_global_message(ws, None)
        data = ws.receive_json()

        assert data == invalid_message


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

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws_admin, connect(normal_user_url) as ws_normal_user:
        ws_admin: WebSocketTestSession
        ws_normal_user: WebSocketTestSession

        # Check connection
        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1 == valid_connection
        assert data_2 == valid_connection

        # Swipe recipes (does not return anything)
        send_swipe(ws_admin, 1, False)
        send_swipe(ws_normal_user, 1, True)

        # Swipe already swipe recipe
        send_swipe(ws_admin, 1, False)
        data_1 = ws_admin.receive_json()

        assert data_1.get("action") == ssae.CONNECTION_CODE
        assert data_1.get("payload").get("status_code") == 409

        # Swipe non existing recipe
        send_swipe(ws_admin, 3, False)
        data_1 = ws_admin.receive_json()

        assert data_1.get("action") == ssae.CONNECTION_CODE
        assert data_1.get("payload").get("status_code") == 404

        # Session message
        send_message(ws_admin, "Message!")

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_MESSAGE
        assert data_1.get("payload").get("message") == "Message!"

        assert data_2.get("action") == ssae.SESSION_MESSAGE
        assert data_2.get("payload").get("message") == "Message!"

        # Send session message
        send_message(ws_normal_user, "Message!")

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_MESSAGE
        assert data_1.get("payload").get("message") == "Message!"

        assert data_2.get("action") == ssae.SESSION_MESSAGE
        assert data_2.get("payload").get("message") == "Message!"

        # Send global message
        send_global_message(ws_admin, "Message!")

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.GLOBAL_MESSAGE
        assert data_1.get("payload").get("message") == "Message!"

        assert data_2.get("action") == ssae.GLOBAL_MESSAGE
        assert data_2.get("payload").get("message") == "Message!"

        # Send unauthorized global message
        send_global_message(ws_normal_user, "Message!")
        data_2 = ws_normal_user.receive_json()

        assert data_2.get("action") == ssae.CONNECTION_CODE
        assert data_2.get("payload").get("status_code") == 401

        # Status update
        send_status_update(ws_admin, sse.PAUSED)

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_1.get("payload").get("status") == sse.PAUSED

        assert data_2.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_2.get("payload").get("status") == sse.PAUSED

        # Unauthorized status update
        send_status_update(ws_normal_user, sse.IN_PROGRESS)
        data_2 = ws_normal_user.receive_json()

        assert data_2.get("action") == ssae.CONNECTION_CODE
        assert data_2.get("payload").get("status_code") == 401

        # Swipe match
        send_swipe(ws_normal_user, 2, True)
        send_swipe(ws_admin, 2, True)

        data_2 = ws_normal_user.receive_json()
        data_1 = ws_admin.receive_json()

        assert data_1.get("action") == ssae.RECIPE_MATCH
        assert data_1.get("payload").get("recipe").get("id") == 2

        assert data_2.get("action") == ssae.RECIPE_MATCH
        assert data_2.get("payload").get("recipe").get("id") == 2
