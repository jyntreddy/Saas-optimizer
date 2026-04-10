"""Negotiation bot models for automated SaaS price reduction"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class NegotiationSession(Base):
    __tablename__ = "negotiation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    vendor = Column(String(255), nullable=False)
    current_price = Column(Float, nullable=False)
    target_price = Column(Float)
    achieved_price = Column(Float)
    
    status = Column(String(50), default="initiated")
    strategy = Column(String(100))
    leverage_points = Column(JSON)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="negotiation_sessions")
    subscription = relationship("Subscription", back_populates="negotiation_sessions")
    communications = relationship("NegotiationCommunication", back_populates="session", cascade="all, delete-orphan")


class NegotiationCommunication(Base):
    __tablename__ = "negotiation_communications"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("negotiation_sessions.id"), nullable=False)
    
    direction = Column(String(20), nullable=False)
    channel = Column(String(50))
    subject = Column(String(500))
    body = Column(Text)
    
    sent_at = Column(DateTime(timezone=True))
    response_received = Column(Boolean, default=False)
    sentiment_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("NegotiationSession", back_populates="communications")


class PriceIntelligence(Base):
    __tablename__ = "price_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String(255), nullable=False, index=True)
    plan_name = Column(String(255))
    
    reported_price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    billing_cycle = Column(String(50))
    
    company_size = Column(String(50))
    industry = Column(String(100))
    negotiated_discount = Column(Float)
    
    submitted_by = Column(Integer, ForeignKey("users.id"))
    verification_status = Column(String(50), default="pending")
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True))
    
    # Relationships
    submitter = relationship("User", foreign_keys=[submitted_by])


class PriceHikePrediction(Base):
    __tablename__ = "price_hike_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String(255), nullable=False)
    
    predicted_date = Column(DateTime(timezone=True))
    confidence = Column(Float)
    expected_increase_pct = Column(Float)
    
    signals = Column(JSON)
    recommendation = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
