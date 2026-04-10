"""Email receipt model for subscription intelligence"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class EmailReceipt(Base):
    __tablename__ = "email_receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_subject = Column(String(500), nullable=False)
    sender_email = Column(String(255), nullable=False)
    received_date = Column(DateTime(timezone=True), nullable=False)
    raw_body = Column(Text, nullable=False)
    
    # Parsed data
    vendor = Column(String(200))
    amount = Column(Float)
    currency = Column(String(10))
    billing_date = Column(DateTime(timezone=True))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    # AI analysis
    category = Column(String(100))  # Productivity, Cloud, Communication, etc.
    confidence_score = Column(Float)  # 0-1.0
    is_subscription = Column(Boolean, default=False)
    extracted_data = Column(JSON)  # Full parsed metadata
    
    # Status
    status = Column(String(50), default="pending")  # pending, matched, ignored, processed
    processed_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="email_receipts")
    subscription = relationship("Subscription", back_populates="email_receipts")
