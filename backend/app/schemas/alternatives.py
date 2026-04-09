"""Subscription Alternative Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionAlternativeBase(BaseModel):
    """Base Subscription Alternative schema"""
    alternative_name: str
    alternative_provider: Optional[str] = None
    alternative_cost: float
    billing_cycle: str = "monthly"
    monthly_savings: Optional[float] = None
    annual_savings: Optional[float] = None
    savings_percentage: Optional[float] = None
    reason: Optional[str] = None
    features_comparison: Optional[str] = None
    recommendation_score: float = 0.0


class SubscriptionAlternativeCreate(SubscriptionAlternativeBase):
    """Create Subscription Alternative schema"""
    subscription_id: int


class SubscriptionAlternative(SubscriptionAlternativeBase):
    """Subscription Alternative response schema"""
    id: int
    subscription_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlternativeSuggestion(BaseModel):
    """Alternative suggestion with subscription details"""
    subscription_id: int
    subscription_name: str
    current_cost: float
    billing_cycle: str
    alternatives: list[SubscriptionAlternative]
    total_potential_savings: float
    best_alternative: Optional[SubscriptionAlternative] = None
