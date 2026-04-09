import pytest
from fastapi import status


def test_create_subscription(client):
    """Test subscription creation"""
    response = client.post(
        "/api/v1/subscriptions/",
        json={
            "service_name": "Netflix",
            "provider": "Netflix Inc",
            "cost": 15.99,
            "billing_cycle": "monthly",
            "status": "active"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["service_name"] == "Netflix"
    assert data["cost"] == 15.99


def test_list_subscriptions(client):
    """Test listing subscriptions"""
    response = client.get("/api/v1/subscriptions/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
