from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.base import Base


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_name = Column(String, nullable=False)
    provider = Column(String)
    cost = Column(Float, nullable=False)
    billing_cycle = Column(String)  # monthly, yearly, etc.
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    start_date = Column(DateTime(timezone=True))
    renewal_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    alternatives = relationship("SubscriptionAlternative", back_populates="subscription", cascade="all, delete-orphan")
    email_receipts = relationship("EmailReceipt", back_populates="subscription", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="subscription", cascade="all, delete-orphan")
    negotiation_sessions = relationship("NegotiationSession", back_populates="subscription", cascade="all, delete-orphan")
