import json
import random
import string

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

token = ""
wallet = ""
second_wallet = ""


def setup():
    global token
    random_username = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    data = {
        "username": random_username
    }
    response = client.post("/user", json=data)
    json_response = json.loads(response.text)
    token = json_response["token"]
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "application/json"
    assert "token" in json_response


def test_add_wallet():
    global wallet
    response = client.post("/wallets", headers={"token": token})
    json_response = json.loads(response.text)
    wallet = json_response["address"]
    assert response.status_code == 200
    assert "address" in json_response
    assert "btc" in json_response
    assert "usd" in json_response


def test_add_second_wallet():
    global second_wallet
    response = client.post("/wallets", headers={"token": token})
    json_response = json.loads(response.text)
    second_wallet = json_response["address"]
    assert response.status_code == 200
    assert "address" in json_response
    assert "btc" in json_response
    assert "usd" in json_response


def test_get_balance():
    response = client.get("/wallets/" + wallet, headers={"token": token})
    json_response = json.loads(response.text)
    get_wallet = json_response["address"]
    assert response.status_code == 200
    assert "address" in json_response
    assert get_wallet == wallet
    assert "btc" in json_response
    assert "usd" in json_response


def test_transactions():
    data = {
        "source_address": wallet,
        "destination_address": second_wallet,
        "value": 50000
    }
    response = client.post("/transactions", headers={"token": token}, json=data)
    response_get_balance = client.get("/wallets/" + wallet, headers={"token": token})
    json_response = json.loads(response_get_balance.text)
    assert response.status_code == 200
    assert json.loads(response.text)['status'] == "Success"
    assert json_response['btc'] == "0.99950000"


def test_list_transactions():
    response = client.get("/transactions", headers={"token": token})
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "application/json"
