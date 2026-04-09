from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from ....db.base import get_db
from ....models.subscription import Subscription

router = APIRouter()


@router.get("/spending-summary")
def get_spending_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get spending summary and analytics"""
    # TODO: Add authentication and filter by current user
    
    total_monthly = db.query(
        func.sum(Subscription.cost)
    ).filter(
        Subscription.billing_cycle == "monthly"
    ).scalar() or 0
    
    total_yearly = db.query(
        func.sum(Subscription.cost)
    ).filter(
        Subscription.billing_cycle == "yearly"
    ).scalar() or 0
    
    subscription_count = db.query(func.count(Subscription.id)).scalar() or 0
    
    return {
        "total_monthly_spend": total_monthly,
        "total_yearly_spend": total_yearly,
        "total_subscriptions": subscription_count,
        "estimated_annual_cost": (total_monthly * 12) + total_yearly
    }


@router.get("/spending-by-category")
def get_spending_by_category(db: Session = Depends(get_db)):
    """Get spending breakdown by category"""
    # TODO: Implement category-based analytics
    pass


@router.get("/trends")
def get_spending_trends(db: Session = Depends(get_db)):
    """Get spending trends over time"""
    # TODO: Implement trend analysis
    pass
