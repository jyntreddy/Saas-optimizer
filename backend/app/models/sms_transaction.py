"""SMS Transaction Model"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class SMSTransaction(Base):
    """Model for storing parsed SMS transactions"""
    
    __tablename__ = "sms_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Twilio data
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False)
    message_sid = Column(String(100), unique=True, index=True)
    raw_message = Column(Text, nullable=False)
    
    # Parsed data
    vendor = Column(String(200))
    amount = Column(Float)
    currency = Column(String(10), default="USD")
    transaction_date = Column(DateTime)
    
    # Subscription matching
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    matched = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="pending")  # pending, processed, ignored, confirmed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sms_transactions")
    subscription = relationship("Subscription", back_populates="sms_transactions")
