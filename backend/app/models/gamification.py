"""Gamification models for SaaS Score and viral loops"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class SaaSScore(Base):
    __tablename__ = "saas_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    score = Column(Integer, default=0)
    level = Column(String(50))
    rank_percentile = Column(Float)
    
    total_savings = Column(Float, default=0.0)
    subscriptions_tracked = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    negotiations_won = Column(Integer, default=0)
    referrals_count = Column(Integer, default=0)
    
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saas_score")
    achievements = relationship("UserAchievement", back_populates="score", cascade="all, delete-orphan")


class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(100))
    
    category = Column(String(100))
    points = Column(Integer, default=0)
    tier = Column(String(50))
    
    requirement_type = Column(String(100))
    requirement_value = Column(Integer)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    score_id = Column(Integer, ForeignKey("saas_scores.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    progress = Column(Integer, default=0)
    
    # Relationships
    score = relationship("SaaSScore", back_populates="achievements")
    achievement = relationship("Achievement")


class SavingsReport(Base):
    __tablename__ = "savings_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    report_type = Column(String(50))
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    total_saved = Column(Float, default=0.0)
    subscriptions_optimized = Column(Integer, default=0)
    duplicates_eliminated = Column(Integer, default=0)
    
    report_data = Column(JSON)
    share_token = Column(String(100), unique=True)
    
    views_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="savings_reports")


class ReferralLink(Base):
    __tablename__ = "referral_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    code = Column(String(50), unique=True, nullable=False)
    clicks = Column(Integer, default=0)
    signups = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    reward_earned = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="referral_links")
