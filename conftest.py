import os
import subprocess
import pytest
from dotenv import load_dotenv

load_dotenv()
os.environ["ENV"] = "test"

from typing import Dict
from app.server import app
from core.db.seed_db import seed_db
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
import asyncio


@pytest.fixture()
def client():
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture()
async def admin_token_headers(client: AsyncClient) -> Dict[str, str]:

    login_data = {
        "username": "admin",
        "password": "admin",
    }
    response = await client.post("/api/latest/users/login", json=login_data)
    response = response.json()
    access_token = response["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
async def normal_user_token_headers(client: AsyncClient) -> Dict[str, str]:

    login_data = {
        "username": "normal_user",
        "password": "normal_user",
    }
    response = await client.post("/api/latest/users/login", json=login_data)
    response = response.json()
    access_token = response["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
async def user_token_headers(client: AsyncClient) -> Dict[str, str]:
    ...


def pytest_addoption(parser):
    parser.addoption("--use-db", action="store", default="False")
    parser.addoption("--no-db-del", action="store", default="False")


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    help_menu = config.getoption("-h")
    if help_menu:
        print("Options:")
        print("\t-h\t\t: Show this menu")
        print(
            "\t--use-db\t: Accepts 'True' or 'False'; 'False' by default;  Use the existing database for testing."
        )
        print(
            "\t--no-db-del\t: Accepts 'True' or 'False'; 'False' by default;  Deletes database after it finishes the tests."
        )
        print()
        print("dont worry about this error :), its made to make this menu look good :D")
        pytest.exit()

    use_db = config.getoption("--use-db")

    if use_db != "True":
        generate_database()


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    ...


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    ...


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """

    # prevent anything from happening when the menu is shown
    help_menu = config.getoption("-h")
    if not help_menu:
        no_db_del = config.getoption("--no-db-del")

        if no_db_del != "True":
            os.remove("test.db")
            print("`test.db` was deleted")


def generate_database():
    if os.path.isfile("test.db"):
        pytest.exit(
            "test.db already exists, remove it to have unpolluted tests. \nor provide `--use-db True` to use the existing database\n\nNOTE! If you also did not provide `--no-db-del True` then `test.db` is now deleted!"
        )

    # Using the shell command, because I could not (bother to)
    # figure out how to create the tables using an engine
    # context manager. Mostly because the session/database
    # setup in this boilerplate is not written by me and I
    # have no clue how to edit it.
    subprocess.run("alembic upgrade head")
    seed_db()


async def ok():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/latest/users")
    return response.json()


async def headers():

    login_data = {
        "username": "admin",
        "password": "admin",
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/latest/users/login", json=login_data)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def get_users(headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/latest/users", headers=headers)

    return response.json()


if __name__ == "__main__":
    # very naughty test to try some functions out
    subprocess.run("alembic upgrade head")
    seed_db()
    print(asyncio.run(ok()))
    headers = asyncio.run(headers())
    print(headers)
    print(asyncio.run(get_users(headers)))
    os.remove("test.db")
