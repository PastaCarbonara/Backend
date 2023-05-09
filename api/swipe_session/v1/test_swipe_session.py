from typing import Dict
from fastapi import Response
from httpx import AsyncClient
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
import pytest
import app.swipe_session.exception.swipe_session as exc

from core.db.enums import SwipeSessionEnum as sse
from core.db.enums import SwipeSessionActionEnum as ssae
from core.exceptions.base import UnauthorizedException
from core.exceptions.recipe import RecipeNotFoundException


def assert_status_code(data, exception):
    assert data.get("action") == ssae.CONNECTION_CODE

    payload = data.get("payload")
    assert payload is not None

    assert payload.get("status_code") == exception.code
    assert payload.get("message") == exception.message


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

    res = fastapi_client.get("/api/v1/groups", headers=headers)
    groups = res.json()

    group_id = groups[0].get("id")
    payload = {"group_id": group_id}
    res = fastapi_client.post(
        f"/api/v1/groups/{group_id}/swipe_sessions", headers=headers, json=payload
    )
    session = res.json()

    assert res.status_code == 200
    assert session.get("group_id") == groups[0].get("id")
    assert len(session.get("swipes")) == 0


@pytest.mark.asyncio
async def test_update_session(
    admin_token_headers: Dict[str, str],
    normal_user_token_headers: Dict[str, str],
    fastapi_client: TestClient,
):
    headers = await admin_token_headers
    user_headers = await normal_user_token_headers

    res = fastapi_client.get("/api/v1/groups", headers=headers)
    groups = res.json()

    group_id = groups[0].get("id")

    res = fastapi_client.get(
        f"/api/v1/groups/{group_id}/swipe_sessions", headers=headers
    )
    sessions = res.json()

    payload = {"id": sessions[0].get("id"), "status": sse.IN_PROGRESS}

    res = fastapi_client.patch(
        f"/api/v1/groups/{group_id}/swipe_sessions", json=payload, headers=user_headers
    )
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

    assert users[0].get("id") is not None, "THE USER DTO MIGHT HAVE CHANGED!!!!"

    # both bad session and user id
    with fastapi_client.websocket_connect("/api/v1/swipe_sessions/1/1") as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert_status_code(data, exc.InvalidIdException)

    # bad user id
    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/{sessions[0].get('id')}/1"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert_status_code(data, exc.InvalidIdException)

    # bad session id
    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/1/{users[0].get('id')}"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert_status_code(data, exc.InvalidIdException)

    # session inactive
    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/{sessions[0].get('id')}/{users[0].get('id')}"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert_status_code(data, exc.SuccessfullConnection)


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
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{normal_user.get('id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(normal_user_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, exc.InvalidIdException)


@pytest.mark.asyncio
async def test_inactive_session(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    res = fastapi_client.get("/api/v1/users", headers=headers)
    users = res.json()

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[1]

    normal_user = users[1]
    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{normal_user.get('id')}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(normal_user_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, exc.InactiveException)


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
    admin_url = f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('id')}"

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, exc.SuccessfullConnection)

        ws.send_text("I am not JSON")
        data = ws.receive_json()

        assert_status_code(data, exc.JSONSerializableException)


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
    admin_url = f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('id')}"

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, exc.SuccessfullConnection)

        ws.send_json({"action": "BANANA"})
        data = ws.receive_json()

        assert_status_code(data, exc.ActionNotFoundException)


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
    admin_url = f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('id')}"

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, exc.SuccessfullConnection)

        send_status_update(ws, "Some status")
        data = ws.receive_json()

        assert_status_code(data, exc.StatusNotFoundException)


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
    admin_url = f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('id')}"

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, exc.SuccessfullConnection)

        send_swipe(ws, "haha recipe ID is not an int", True)
        data = ws.receive_json()

        assert data.get("action") == ssae.CONNECTION_CODE
        assert data.get("payload").get("status_code") == 400
        assert type(data.get("payload").get("message")) == str


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
    admin_url = f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('id')}"

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(admin_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, exc.SuccessfullConnection)

        send_message(ws, None)
        data = ws.receive_json()

        assert_status_code(data, exc.NoMessageException)

        send_global_message(ws, None)
        data = ws.receive_json()

        assert_status_code(data, exc.NoMessageException)


@pytest.mark.asyncio
async def test_update_session_to_active(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    assert sessions[1].get("status") == sse.READY
    assert sessions[2].get("status") == sse.READY

    payload = {"id": sessions[2].get("id"), "status": sse.IN_PROGRESS}
    res = fastapi_client.patch(
        f"/api/v1/groups/{sessions[2].get('group_id')}/swipe_sessions",
        json=payload,
        headers=headers,
    )

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    assert sessions[1].get("status") == sse.READY
    assert sessions[2].get("status") == sse.IN_PROGRESS

    payload = {"id": sessions[1].get("id"), "status": sse.IN_PROGRESS}
    res = fastapi_client.patch(
        f"/api/v1/groups/{sessions[1].get('group_id')}/swipe_sessions",
        json=payload,
        headers=headers,
    )

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    assert sessions[1].get("status") == sse.IN_PROGRESS
    assert sessions[2].get("status") == sse.PAUSED


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
    admin_url = f"/api/v1/swipe_sessions/{cur_session.get('id')}/{admin.get('id')}"

    normal_user = users[1]
    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}/{normal_user.get('id')}"
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

        assert_status_code(data_1, exc.SuccessfullConnection)
        assert_status_code(data_2, exc.SuccessfullConnection)

        # Swipe recipes (does not return anything)
        send_swipe(ws_admin, 1, False)
        send_swipe(ws_normal_user, 1, True)

        # Swipe already swipe recipe
        send_swipe(ws_admin, 1, False)
        data_1 = ws_admin.receive_json()

        assert_status_code(data_1, exc.AlreadySwipedException)

        # Swipe non existing recipe
        send_swipe(ws_admin, 999, False)
        data_1 = ws_admin.receive_json()

        assert_status_code(data_1, RecipeNotFoundException)

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

        assert_status_code(data_2, UnauthorizedException)

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

        assert_status_code(data_2, UnauthorizedException)

        # Swipe match
        send_swipe(ws_normal_user, 2, True)
        send_swipe(ws_admin, 2, True)

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.RECIPE_MATCH
        assert data_1.get("payload").get("recipe").get("id") == 2

        assert data_2.get("action") == ssae.RECIPE_MATCH
        assert data_2.get("payload").get("recipe").get("id") == 2
        
        # should be closing

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_1.get("payload").get("status") == sse.COMPLETED

        assert data_2.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_2.get("payload").get("status") == sse.COMPLETED
