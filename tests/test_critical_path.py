from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'project')))
from app import app

client = TestClient(app)

def test_register_user():
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201 or response.status_code == 200
    assert "username" in response.json() or "message" in response.json()

def test_fund_account():
    # First register user and authenticate
    client.post("/register", json={"username": "testuser2", "password": "testpass"})
    auth = ("testuser2", "testpass")
    response = client.post("/fund", auth=auth, json={"amt": 1000})
    assert response.status_code == 200
    assert "balance" in response.json()

def test_pay_another_user():
    # Register two users
    client.post("/register", json={"username": "payer", "password": "testpass"})
    client.post("/register", json={"username": "payee", "password": "testpass"})
    auth = ("payer", "testpass")
    # Fund payer account first
    client.post("/fund", auth=auth, json={"amt": 1000})
    # Pay payee
    response = client.post("/pay", auth=auth, json={"to": "payee", "amt": 500})
    assert response.status_code == 200
    assert "balance" in response.json()

def test_check_balance():
    client.post("/register", json={"username": "balanceuser", "password": "testpass"})
    auth = ("balanceuser", "testpass")
    client.post("/fund", auth=auth, json={"amt": 1000})
    response = client.get("/bal?currency=USD", auth=auth)
    assert response.status_code == 200
    assert "balance" in response.json()

def test_transaction_history():
    client.post("/register", json={"username": "historyuser", "password": "testpass"})
    auth = ("historyuser", "testpass")
    client.post("/fund", auth=auth, json={"amt": 1000})
    response = client.get("/stmt", auth=auth)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_product():
    client.post("/register", json={"username": "productuser", "password": "testpass"})
    auth = ("productuser", "testpass")
    response = client.post("/product", auth=auth, json={"name": "Test Product", "price": 100, "description": "Test description"})
    assert response.status_code == 201 or response.status_code == 200
    assert "id" in response.json()

def test_list_products():
    response = client.get("/product")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_buy_product():
    client.post("/register", json={"username": "buyer", "password": "testpass"})
    auth = ("buyer", "testpass")
    # Add product
    product_response = client.post("/product", auth=auth, json={"name": "Buy Product", "price": 100, "description": "Buy description"})
    product_id = product_response.json().get("id")
    # Fund buyer account
    client.post("/fund", auth=auth, json={"amt": 200})
    # Buy product
    response = client.post("/buy", auth=auth, json={"product_id": product_id})
    assert response.status_code == 200
    assert "message" in response.json()
