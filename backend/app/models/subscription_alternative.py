"""Subscription Alternative Model"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class SubscriptionAlternative(Base):
    """Model for storing alternative subscription suggestions"""
    
    __tablename__ = "subscription_alternatives"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Alternative details
    alternative_name = Column(String(200), nullable=False)
    alternative_provider = Column(String(200))
    alternative_cost = Column(Float, nullable=False)
    billing_cycle = Column(String(50), default="monthly")
    
    # Savings
    monthly_savings = Column(Float)
    annual_savings = Column(Float)
    savings_percentage = Column(Float)
    
    # Recommendation details
    reason = Column(Text)
    features_comparison = Column(Text)
    recommendation_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="alternatives")
