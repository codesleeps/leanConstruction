import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_read_main():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 404  # No root endpoint defined yet


def test_create_user():
    """Test user creation"""
    response = client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "company": "Test Company",
            "role": "manager"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["message"] == "User created successfully"


def test_create_duplicate_user():
    """Test duplicate user creation fails"""
    # First user
    client.post(
        "/users/",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "company": "Test Company",
            "role": "manager"
        }
    )
    
    # Duplicate user
    response = client.post(
        "/users/",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "company": "Test Company",
            "role": "manager"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login():
    """Test user login"""
    # Create user first
    client.post(
        "/users/",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
            "full_name": "Login User",
            "company": "Test Company",
            "role": "manager"
        }
    )
    
    # Login
    response = client.post(
        "/token",
        data={
            "username": "login@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    response = client.get("/users/me")
    assert response.status_code == 401


# Cleanup
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    Base.metadata.drop_all(bind=engine)
