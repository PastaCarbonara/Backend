import os
import subprocess
import pytest
from dotenv import load_dotenv

load_dotenv()
os.environ["ENV"] = "test"

from fastapi.testclient import TestClient
from app.server import app
from core.db.seed_db import seed_db

test_client = TestClient(app)


@pytest.fixture(scope="session")
def client():
    return test_client


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
