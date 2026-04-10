"""Team member and usage tracking models"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(100))
    department = Column(String(100))
    
    is_active = Column(Boolean, default=True)
    joined_date = Column(DateTime(timezone=True))
    left_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("User", back_populates="team_members")
    usage_logs = relationship("UsageLog", back_populates="team_member", cascade="all, delete-orphan")


class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    team_member_id = Column(Integer, ForeignKey("team_members.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    usage_date = Column(DateTime(timezone=True), nullable=False)
    activity_type = Column(String(100))
    duration_minutes = Column(Integer)
    activity_count = Column(Integer, default=1)
    activity_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    team_member = relationship("TeamMember", back_populates="usage_logs")
    subscription = relationship("Subscription", back_populates="usage_logs")


class ShadowITDetection(Base):
    __tablename__ = "shadow_it_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_member_id = Column(Integer, ForeignKey("team_members.id"))
    
    tool_name = Column(String(255), nullable=False)
    vendor = Column(String(255))
    detected_from = Column(String(100))
    estimated_cost = Column(Float)
    currency = Column(String(10))
    
    risk_level = Column(String(50))
    risk_reasons = Column(JSON)
    
    status = Column(String(50), default="detected")
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("User", foreign_keys=[organization_id])
    team_member = relationship("TeamMember")
