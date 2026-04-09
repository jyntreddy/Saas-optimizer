import pytest
from fastapi import status


def test_create_user(client):
    """Test user creation"""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_create_duplicate_user(client):
    """Test duplicate user creation fails"""
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    # Create first user
    client.post("/api/v1/users/", json=user_data)
    
    # Try to create duplicate
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
