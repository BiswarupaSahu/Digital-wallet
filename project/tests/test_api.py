import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db, Base
from app import app
from models import User, Product

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Basic dGVzdHVzZXI6dGVzdHBhc3M="}  # testuser:testpass

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_user_registration(client):
    """Test user registration"""
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    data = response.json()
    assert "message" in data

def test_duplicate_registration(client):
    """Test duplicate user registration"""
    # Register first user
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    
    # Try to register same username
    response = client.post("/register", json={"username": "testuser", "password": "testpass2"})
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["error"]

def test_fund_account(client, auth_headers):
    """Test funding account"""
    # Register user first
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    
    # Fund account
    response = client.post("/fund", json={"amt": 1000}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 1000.0

def test_check_balance(client, auth_headers):
    """Test checking balance"""
    # Register and fund
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    client.post("/fund", json={"amt": 1000}, headers=auth_headers)
    
    # Check balance
    response = client.get("/bal", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 1000.0
    assert data["currency"] == "INR"

def test_add_product(client, auth_headers):
    """Test adding product"""
    # Register user first
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    
    # Add product
    response = client.post("/product", json={
        "name": "Test Product",
        "price": 99.99,
        "description": "A test product"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["message"] == "Product added"

def test_list_products(client):
    """Test listing products"""
    response = client.get("/product")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_authentication_required(client):
    """Test that protected endpoints require authentication"""
    endpoints = [
        ("POST", "/fund", {"amt": 100}),
        ("POST", "/pay", {"to": "user", "amt": 100}),
        ("GET", "/bal", None),
        ("GET", "/stmt", None),
        ("POST", "/buy", {"product_id": 1}),
        ("POST", "/product", {"name": "Test", "price": 100})
    ]
    
    for method, endpoint, json_data in endpoints:
        if method == "POST":
            response = client.post(endpoint, json=json_data)
        else:
            response = client.get(endpoint)
        
        assert response.status_code == 401

def test_invalid_data_validation(client, auth_headers):
    """Test input validation"""
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    
    # Test invalid amount
    response = client.post("/fund", json={"amt": -100}, headers=auth_headers)
    assert response.status_code == 422  # FastAPI validation error
    
    # Test invalid username in registration
    response = client.post("/register", json={"username": "ab", "password": "testpass"})
    assert response.status_code == 422