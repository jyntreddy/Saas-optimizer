"""API client for communicating with FastAPI backend"""

import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_URL = os.getenv("BACKEND_URL", os.getenv("API_URL", "http://localhost:8000"))
API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
BASE_URL = f"{API_URL}{API_V1_PREFIX}"


def get_api_url() -> str:
    """Get the API URL"""
    return API_URL


def test_connection() -> bool:
    """Test connection to the API"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def login(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Login and get access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """Get current user information"""
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Get user error: {e}")
        return None


def create_user(email: str, password: str, full_name: str = None) -> Optional[Dict[str, Any]]:
    """Create a new user"""
    try:
        data = {"email": email, "password": password}
        if full_name:
            data["full_name"] = full_name
            
        response = requests.post(f"{BASE_URL}/users/", json=data)
        if response.status_code == 201:
            return response.json()
        return None
    except Exception as e:
        print(f"Create user error: {e}")
        return None


def get_subscriptions(token: str) -> List[Dict[str, Any]]:
    """Get all subscriptions"""
    try:
        response = requests.get(
            f"{BASE_URL}/subscriptions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Get subscriptions error: {e}")
        return []


def create_subscription(token: str, subscription: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a new subscription"""
    try:
        response = requests.post(
            f"{BASE_URL}/subscriptions/",
            json=subscription,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 201:
            return response.json()
        return None
    except Exception as e:
        print(f"Create subscription error: {e}")
        return None


def update_subscription(token: str, subscription_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a subscription"""
    try:
        response = requests.put(
            f"{BASE_URL}/subscriptions/{subscription_id}",
            json=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Update subscription error: {e}")
        return None


def delete_subscription(token: str, subscription_id: int) -> bool:
    """Delete a subscription"""
    try:
        response = requests.delete(
            f"{BASE_URL}/subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 204
    except Exception as e:
        print(f"Delete subscription error: {e}")
        return False


def get_spending_summary(token: str) -> Optional[Dict[str, Any]]:
    """Get spending summary"""
    try:
        response = requests.get(
            f"{BASE_URL}/analytics/spending-summary",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Get spending summary error: {e}")
        return None


def get_recommendations(token: str) -> List[Dict[str, Any]]:
    """Get cost saving recommendations"""
    try:
        response = requests.get(
            f"{BASE_URL}/recommendations/cost-savings",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Get recommendations error: {e}")
        return []


def get_subscription_summary(token: str) -> Optional[Dict[str, Any]]:
    """Get comprehensive subscription summary with duplicates and low-usage detection"""
    try:
        response = requests.get(
            f"{BASE_URL}/subscriptions/summary",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Get subscription summary error: {e}")
        return None


def get_subscription_alternatives(token: str) -> List[Dict[str, Any]]:
    """Get alternative subscription suggestions with savings"""
    try:
        response = requests.get(
            f"{BASE_URL}/subscriptions/alternatives",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Get alternatives error: {e}")
        return []


def get_sms_transactions(token: str, status: str = None) -> List[Dict[str, Any]]:
    """Get SMS transactions"""
    try:
        url = f"{BASE_URL}/sms/transactions"
        if status:
            url += f"?status={status}"
        
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Get SMS transactions error: {e}")
        return []


def update_sms_status(token: str, transaction_id: int, status: str) -> bool:
    """Update SMS transaction status (confirmed/ignored)"""
    try:
        response = requests.patch(
            f"{BASE_URL}/sms/transactions/{transaction_id}/status",
            params={"status": status},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Update SMS status error: {e}")
        return False


def create_subscription_from_sms(token: str, transaction_id: int) -> Optional[Dict[str, Any]]:
    """Create a subscription from an SMS transaction"""
    try:
        response = requests.post(
            f"{BASE_URL}/sms/transactions/{transaction_id}/create-subscription",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Create subscription from SMS error: {e}")
        return None
