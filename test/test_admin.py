import json
import os

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_statistic():
    response = client.get("/statistics", headers={"token": os.getenv("ADMIN_TOKEN")})
    json_response = json.loads(response.text)
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "application/json"
    assert "total transactions" in json_response
    assert "platform profit" in json_response
