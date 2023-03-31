from fastapi import Response
import pytest


def test_pytest(client):
    response: Response = client.get("/api/v1/health")

    assert response.status_code == 200
