from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    sms_transactions = relationship("SMSTransaction", back_populates="user", cascade="all, delete-orphan")
    email_receipts = relationship("EmailReceipt", back_populates="user", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="organization", cascade="all, delete-orphan")
    negotiation_sessions = relationship("NegotiationSession", back_populates="user", cascade="all, delete-orphan")
    saas_score = relationship("SaaSScore", back_populates="user", uselist=False, cascade="all, delete-orphan")
    savings_reports = relationship("SavingsReport", back_populates="user", cascade="all, delete-orphan")
    referral_links = relationship("ReferralLink", back_populates="user", cascade="all, delete-orphan")
    gmail_token = relationship("GmailToken", back_populates="user", uselist=False, cascade="all, delete-orphan")
