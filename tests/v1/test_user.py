import pytest
from fastapi.testclient import TestClient

from dotenv import load_dotenv
load_dotenv()

from app.server import app
client = TestClient(app)


@pytest.mark.asyncio
async def test_pytest():
    import os
    assert os.getenv("HASH_MIN_LEN") == "16", "env not loaded"
    
    assert 1 + 1 == 2, "Math gone wrong!?"
    assert 1 + 2 == 3, "Bad test!"

@pytest.mark.asyncio
async def the_thing():
    assert "bad" == "good", "D:" 


@pytest.mark.asyncio
async def test_the_thing():
    assert "owo" == "UWU", "D:" 