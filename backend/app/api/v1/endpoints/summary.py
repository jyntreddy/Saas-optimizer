"""Subscription Summary and Analysis Endpoint"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.db.base import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/summary")
async def get_subscription_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive subscription summary with analysis
    
    Includes:
    - Total spend aggregation
    - Duplicate detection
    - Low-usage detection
    - Spending trends
    """
    
    # Get all active subscriptions
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).all()
    
    # Calculate total spending
    total_monthly = sum(
        sub.cost if sub.billing_cycle == "monthly" else
        sub.cost / 12 if sub.billing_cycle == "yearly" else
        sub.cost / 3 if sub.billing_cycle == "quarterly" else
        sub.cost
        for sub in subscriptions
    )
    
    total_annual = sum(
        sub.cost * 12 if sub.billing_cycle == "monthly" else
        sub.cost if sub.billing_cycle == "yearly" else
        sub.cost * 4 if sub.billing_cycle == "quarterly" else
        sub.cost * 12
        for sub in subscriptions
    )
    
    # Detect duplicates (similar service names)
    duplicates = _detect_duplicates(subscriptions)
    
    # Detect low-usage subscriptions (no recent SMS transactions)
    low_usage = _detect_low_usage(subscriptions, db)
    
    # Get spending by category
    spending_by_provider = {}
    for sub in subscriptions:
        provider = sub.provider or sub.service_name
        if provider not in spending_by_provider:
            spending_by_provider[provider] = 0
        
        monthly_cost = (
            sub.cost if sub.billing_cycle == "monthly" else
            sub.cost / 12 if sub.billing_cycle == "yearly" else
            sub.cost / 3 if sub.billing_cycle == "quarterly" else
            sub.cost
        )
        spending_by_provider[provider] += monthly_cost
    
    # Calculate trends (last 3 months mock data)
    trends = _calculate_spending_trends(subscriptions)
    
    return {
        "total_subscriptions": len(subscriptions),
        "active_subscriptions": len([s for s in subscriptions if s.status == "active"]),
        "total_monthly_spend": round(total_monthly, 2),
        "total_annual_spend": round(total_annual, 2),
        "average_subscription_cost": round(total_monthly / len(subscriptions), 2) if subscriptions else 0,
        "spending_by_provider": spending_by_provider,
        "duplicates": duplicates,
        "low_usage_subscriptions": low_usage,
        "spending_trends": trends,
        "recommendations_count": len(duplicates) + len(low_usage),
        "potential_savings": sum(d["potential_savings"] for d in duplicates) + sum(l["monthly_cost"] for l in low_usage)
    }


@router.get("/duplicates")
async def get_duplicate_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Detect and return duplicate or similar subscriptions
    """
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).all()
    
    return _detect_duplicates(subscriptions)


@router.get("/low-usage")
async def get_low_usage_subscriptions(
    days: int = Query(default=60, ge=30, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Detect subscriptions with low or no usage
    """
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).all()
    
    return _detect_low_usage(subscriptions, db, days)


def _detect_duplicates(subscriptions: List[Subscription]) -> List[Dict[str, Any]]:
    """Detect duplicate or similar subscriptions"""
    duplicates = []
    seen_services = {}
    
    # Common similar services
    similar_groups = [
        {"netflix", "hulu", "disney", "prime video", "hbo max"},
        {"spotify", "apple music", "youtube music", "amazon music"},
        {"dropbox", "google drive", "onedrive", "icloud"},
        {"zoom", "google meet", "microsoft teams", "webex"},
        {"slack", "microsoft teams", "discord"},
    ]
    
    for sub in subscriptions:
        service_lower = sub.service_name.lower()
        
        # Check for exact duplicates
        if service_lower in seen_services:
            duplicates.append({
                "subscription_id": sub.id,
                "service_name": sub.service_name,
                "duplicate_of": seen_services[service_lower]["service_name"],
                "duplicate_of_id": seen_services[service_lower]["id"],
                "type": "exact_duplicate",
                "monthly_cost": sub.cost if sub.billing_cycle == "monthly" else sub.cost / 12,
                "potential_savings": sub.cost if sub.billing_cycle == "monthly" else sub.cost / 12,
                "recommendation": f"You have multiple {sub.service_name} subscriptions. Consider keeping only one."
            })
        else:
            seen_services[service_lower] = {"id": sub.id, "service_name": sub.service_name}
        
        # Check for similar services
        for group in similar_groups:
            if any(service in service_lower for service in group):
                # Check if user has multiple services in this group
                user_services_in_group = [
                    s for s in subscriptions
                    if any(srv in s.service_name.lower() for srv in group)
                ]
                
                if len(user_services_in_group) > 1:
                    # Only add if not already in duplicates
                    if sub.id not in [d["subscription_id"] for d in duplicates]:
                        monthly_cost = sub.cost if sub.billing_cycle == "monthly" else sub.cost / 12
                        duplicates.append({
                            "subscription_id": sub.id,
                            "service_name": sub.service_name,
                            "type": "similar_service",
                            "category": list(group)[0].title() + " alternatives",
                            "monthly_cost": monthly_cost,
                            "potential_savings": monthly_cost * 0.5,  # Estimate 50% savings by consolidating
                            "recommendation": f"You have multiple streaming/storage services. Consider consolidating to save money.",
                            "similar_services": [s.service_name for s in user_services_in_group if s.id != sub.id]
                        })
    
    return duplicates


def _detect_low_usage(subscriptions: List[Subscription], db: Session, days: int = 60) -> List[Dict[str, Any]]:
    """Detect subscriptions with low usage based on SMS transactions"""
    low_usage = []
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    for sub in subscriptions:
        # Check for recent SMS transactions
        transaction_count = db.query(SMSTransaction).filter(
            SMSTransaction.subscription_id == sub.id,
            SMSTransaction.created_at >= cutoff_date
        ).count()
        
        # If no transactions in the period, mark as low usage
        if transaction_count == 0:
            monthly_cost = sub.cost if sub.billing_cycle == "monthly" else sub.cost / 12
            
            low_usage.append({
                "subscription_id": sub.id,
                "service_name": sub.service_name,
                "monthly_cost": monthly_cost,
                "billing_cycle": sub.billing_cycle,
                "last_transaction": None,
                "days_since_last_use": days,
                "transaction_count": 0,
                "recommendation": f"No usage detected in the last {days} days. Consider canceling to save ${monthly_cost:.2f}/month."
            })
    
    return low_usage


def _calculate_spending_trends(subscriptions: List[Subscription]) -> Dict[str, List[float]]:
    """Calculate spending trends over time (mock data for now)"""
    # In production, this would query actual transaction history
    
    total_monthly = sum(
        sub.cost if sub.billing_cycle == "monthly" else sub.cost / 12
        for sub in subscriptions
    )
    
    # Generate last 6 months trend (mock variation)
    import random
    trends = []
    for i in range(6):
        variation = random.uniform(0.85, 1.15)
        trends.insert(0, round(total_monthly * variation, 2))
    
    return {
        "months": ["6 months ago", "5 months ago", "4 months ago", "3 months ago", "2 months ago", "Last month"],
        "spending": trends
    }
