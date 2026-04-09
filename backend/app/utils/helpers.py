from datetime import datetime, timedelta
from typing import Optional


def calculate_next_renewal(start_date: datetime, billing_cycle: str) -> datetime:
    """Calculate next renewal date based on billing cycle"""
    if billing_cycle == "monthly":
        return start_date + timedelta(days=30)
    elif billing_cycle == "yearly":
        return start_date + timedelta(days=365)
    elif billing_cycle == "quarterly":
        return start_date + timedelta(days=90)
    else:
        return start_date + timedelta(days=30)


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}" if currency == "USD" else f"{amount:,.2f} {currency}"


def calculate_annual_cost(cost: float, billing_cycle: str) -> float:
    """Calculate annual cost from subscription cost"""
    if billing_cycle == "monthly":
        return cost * 12
    elif billing_cycle == "yearly":
        return cost
    elif billing_cycle == "quarterly":
        return cost * 4
    else:
        return cost * 12
