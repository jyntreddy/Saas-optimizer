"""Formatting utilities"""

from datetime import datetime
from typing import Optional


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def format_date(date_str: Optional[str]) -> str:
    """Format date string"""
    if not date_str:
        return "N/A"
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime("%B %d, %Y")
    except:
        return date_str


def calculate_annual_cost(cost: float, billing_cycle: str) -> float:
    """Calculate annual cost from subscription cost"""
    billing_cycle = billing_cycle.lower() if billing_cycle else "monthly"
    
    if billing_cycle == "monthly":
        return cost * 12
    elif billing_cycle == "yearly":
        return cost
    elif billing_cycle == "quarterly":
        return cost * 4
    else:
        return cost * 12


def get_status_color(status: str) -> str:
    """Get color for subscription status"""
    status = status.lower() if status else ""
    
    colors = {
        "active": "🟢",
        "cancelled": "🔴",
        "expired": "⚫",
        "trial": "🟡"
    }
    
    return colors.get(status, "⚪")
