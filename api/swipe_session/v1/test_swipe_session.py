# pylint: skip-file
import pytest

from typing import Dict
from httpx import AsyncClient
from fastapi import Response
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

import core.exceptions.websocket as exc
from core.db.enums import SwipeSessionEnum as sse
from core.db.enums import SwipeSessionActionEnum as ssae
from core.exceptions.base import UnauthorizedException
from app.recipe.exceptions.recipe import RecipeNotFoundException


def assert_status_code(data, exception):
    assert data.get("action") == ssae.CONNECTION_CODE

    payload = data.get("payload")
    assert payload is not None

    assert payload.get("status_code") == exception.code
    assert payload.get("message") == exception.message


def strip_headers(header: str):
    return header.get("Authorization").split(" ")[1]


def send_swipe(ws: WebSocketTestSession, recipe_id: int, like: bool):
    packet = {
        "action": ssae.RECIPE_SWIPE,
        "payload": {"recipe_id": recipe_id, "like": like},
    }
    ws.send_json(packet)


def send_message(ws: WebSocketTestSession, message: str):
    packet = {"action": ssae.POOL_MESSAGE, "payload": {"message": message}}
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

    assert len(docs.get("actions")) == len([action.value for action in ssae])
    for action in ssae:
        assert action.value in [action for action in docs.get("actions")]


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
    swipe_sessions = res.json()

    assert res.status_code == 200
    assert len(swipe_sessions) == 3
    assert not any(i.get("status") != sse.READY for i in swipe_sessions)


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
    fastapi_client: TestClient,
):
    headers = await admin_token_headers

    res = fastapi_client.get("/api/v1/groups", headers=headers)
    groups = res.json()

    group_id = groups[0].get("id")

    res = fastapi_client.get(
        f"/api/v1/groups/{group_id}/swipe_sessions", headers=headers
    )
    swipe_sessions = res.json()

    payload = {"id": swipe_sessions[0].get("id"), "status": sse.IN_PROGRESS}

    res = fastapi_client.patch(
        f"/api/v1/groups/{group_id}/swipe_sessions", json=payload, headers=headers
    )
    swipe_session = res.json()

    assert res.status_code == 200
    assert swipe_session.get("status") != swipe_sessions[0].get("status")
    assert swipe_session.get("status") == sse.IN_PROGRESS


@pytest.mark.asyncio
async def test_websocket_invalid_id(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
):
    headers = await admin_token_headers

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    # both bad session and user id
    with fastapi_client.websocket_connect("/api/v1/swipe_sessions/1?token=1") as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert_status_code(data, UnauthorizedException)

    # bad session id
    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/1?token={strip_headers(headers)}"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert_status_code(data, exc.InvalidIdException)

    # session inactive
    with fastapi_client.websocket_connect(
        f"/api/v1/swipe_sessions/{swipe_sessions[0].get('id')}?token={strip_headers(headers)}"
    ) as ws:
        ws: WebSocketTestSession
        data = ws.receive_json()

        assert_status_code(data, exc.SuccessfullConnection)


@pytest.mark.asyncio
async def test_not_in_group(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
    normal_user_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    normal_headers = await normal_user_token_headers

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    cur_session = swipe_sessions[0]

    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}"
        f"?token={strip_headers(normal_headers)}"
    )

    # i just want the context manager to fit on a single line :,)
    connect = fastapi_client.websocket_connect

    # NOTE to self: receive() functions wait until they receive any data
    # and if they do not receive anything, they wait 'til the end of time
    with connect(normal_user_url) as ws:
        ws: WebSocketTestSession

        data = ws.receive_json()

        assert_status_code(data, UnauthorizedException)


@pytest.mark.asyncio
async def test_inactive_session(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
    normal_user_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    normal_headers = await normal_user_token_headers

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    cur_session = swipe_sessions[1]

    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}"
        f"?token={strip_headers(normal_headers)}"
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

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    cur_session = swipe_sessions[0]

    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

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

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    cur_session = swipe_sessions[0]

    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

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

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    cur_session = swipe_sessions[0]

    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

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

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    cur_session = swipe_sessions[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

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

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    cur_session = swipe_sessions[0]
    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

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
    swipe_sessions = res.json()

    assert swipe_sessions[1].get("status") == sse.READY
    assert swipe_sessions[2].get("status") == sse.READY

    payload = {"id": swipe_sessions[2].get("id"), "status": sse.IN_PROGRESS}
    res = fastapi_client.patch(
        f"/api/v1/groups/{swipe_sessions[2].get('group_id')}/swipe_sessions",
        json=payload,
        headers=headers,
    )

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    assert swipe_sessions[1].get("status") == sse.READY
    assert swipe_sessions[2].get("status") == sse.IN_PROGRESS

    payload = {"id": swipe_sessions[1].get("id"), "status": sse.IN_PROGRESS}
    res = fastapi_client.patch(
        f"/api/v1/groups/{swipe_sessions[1].get('group_id')}/swipe_sessions",
        json=payload,
        headers=headers,
    )

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    swipe_sessions = res.json()

    assert swipe_sessions[1].get("status") == sse.IN_PROGRESS
    assert swipe_sessions[2].get("status") == sse.PAUSED


@pytest.mark.asyncio
async def test_swipe_session_1(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
    normal_user_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    normal_headers = await normal_user_token_headers

    res = fastapi_client.get("/api/v1/users", headers=headers)

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[1]

    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}"
        f"?token={strip_headers(normal_headers)}"
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

        # Get recipes
        ws_admin.send_json({"action": ssae.GET_RECIPES})
        data_1 = ws_admin.receive_json()

        assert data_1.get("action") == ssae.GET_RECIPES

        payload_1 = data_1.get("payload")
        assert payload_1 is not None
        assert type(payload_1.get("recipes")) == list

        ws_normal_user.send_json({"action": ssae.GET_RECIPES})
        data_2 = ws_normal_user.receive_json()

        assert data_2.get("action") == ssae.GET_RECIPES

        payload_2 = data_2.get("payload")
        assert payload_2 is not None
        assert type(payload_2.get("recipes")) == list

        admin_recipes = payload_1.get("recipes")
        user_recipes = payload_2.get("recipes")

        # Swipe recipes (does not return anything)
        for recipe in admin_recipes:
            send_swipe(ws_admin, recipe["id"], True)

        for recipe in user_recipes:
            send_swipe(ws_normal_user, recipe["id"], True)

        # Swipe already swipe recipe
        send_swipe(ws_admin, 1, False)
        data_1 = ws_admin.receive_json()

        assert_status_code(data_1, exc.AlreadySwipedException)

        # Swipe non existing recipe
        send_swipe(ws_admin, 999, False)
        data_1 = ws_admin.receive_json()

        assert_status_code(data_1, RecipeNotFoundException)


@pytest.mark.asyncio
async def test_swipe_session_2(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
    normal_user_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    normal_headers = await normal_user_token_headers

    res = fastapi_client.get("/api/v1/users", headers=headers)

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[1]

    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}"
        f"?token={strip_headers(normal_headers)}"
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

        # Session message
        send_message(ws_admin, "Message!")

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.POOL_MESSAGE
        assert data_1.get("payload").get("message") == "Message!"

        assert data_2.get("action") == ssae.POOL_MESSAGE
        assert data_2.get("payload").get("message") == "Message!"

        # Send session message
        send_message(ws_normal_user, "Message!")

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.POOL_MESSAGE
        assert data_1.get("payload").get("message") == "Message!"

        assert data_2.get("action") == ssae.POOL_MESSAGE
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


@pytest.mark.asyncio
async def test_swipe_session_3(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
    normal_user_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    normal_headers = await normal_user_token_headers

    res = fastapi_client.get("/api/v1/users", headers=headers)

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[1]

    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}"
        f"?token={strip_headers(normal_headers)}"
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

        # Status update
        send_status_update(ws_admin, sse.PAUSED)

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_1.get("payload").get("status") == sse.PAUSED

        assert data_2.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_2.get("payload").get("status") == sse.PAUSED

        # Status update, refert it so it keeps working.
        send_status_update(ws_admin, sse.IN_PROGRESS)

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_1.get("payload").get("status") == sse.IN_PROGRESS

        assert data_2.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_2.get("payload").get("status") == sse.IN_PROGRESS

        # Unauthorized status update
        send_status_update(ws_normal_user, sse.IN_PROGRESS)
        data_2 = ws_normal_user.receive_json()

        assert_status_code(data_2, UnauthorizedException)


@pytest.mark.asyncio
async def test_swipe_session_4(
    fastapi_client: TestClient,
    admin_token_headers: Dict[str, str],
    normal_user_token_headers: Dict[str, str],
):
    headers = await admin_token_headers
    normal_headers = await normal_user_token_headers

    res = fastapi_client.get("/api/v1/users", headers=headers)

    res = fastapi_client.get("/api/v1/swipe_sessions", headers=headers)
    sessions = res.json()

    cur_session = sessions[1]

    admin_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}?token={strip_headers(headers)}"
    )

    normal_user_url = (
        f"/api/v1/swipe_sessions/{cur_session.get('id')}"
        f"?token={strip_headers(normal_headers)}"
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

        # Get new recipes for user
        ws_normal_user.send_json({"action": ssae.GET_RECIPES})
        data_2 = ws_normal_user.receive_json()

        assert data_2.get("action") == ssae.GET_RECIPES

        payload_2 = data_2.get("payload")
        assert payload_2 is not None
        assert type(payload_2.get("recipes")) == list

        user_recipes = payload_2.get("recipes")
        # Swipe match
        send_swipe(ws_normal_user, user_recipes[0]["id"], True)

        # should be closing

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.RECIPE_MATCH
        assert data_1.get("payload").get("recipe").get("id") == user_recipes[0]["id"]

        assert data_2.get("action") == ssae.RECIPE_MATCH
        assert data_2.get("payload").get("recipe").get("id") == user_recipes[0]["id"]

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert data_1.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_1.get("payload").get("status") == sse.COMPLETED

        assert data_2.get("action") == ssae.SESSION_STATUS_UPDATE
        assert data_2.get("payload").get("status") == sse.COMPLETED

        data_1 = ws_admin.receive_json()
        data_2 = ws_normal_user.receive_json()

        assert_status_code(data_1, exc.ClosingConnection)
        assert_status_code(data_2, exc.ClosingConnection)
