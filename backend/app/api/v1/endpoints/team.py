"""Team tracking and shadow IT endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ....db.base import get_db
from app.api.dependencies import get_current_user
from ....models import User, Subscription
from ....models.team import TeamMember, UsageLog, ShadowITDetection
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()


class TeamMemberCreate(BaseModel):
    email: str
    full_name: str | None = None
    role: str | None = None
    department: str | None = None


class UsageLogCreate(BaseModel):
    team_member_id: int
    subscription_id: int
    usage_date: datetime
    activity_type: str | None = None
    duration_minutes: int | None = None


class TeamMemberResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: str | None
    department: str | None
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/members", response_model=TeamMemberResponse)
def add_team_member(
    member_data: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add team member"""
    
    member = TeamMember(
        organization_id=current_user.id,
        **member_data.model_dump()
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return member


@router.get("/members", response_model=List[TeamMemberResponse])
def get_team_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all team members"""
    
    members = db.query(TeamMember).filter(
        TeamMember.organization_id == current_user.id,
        TeamMember.is_active == True
    ).all()
    
    return members


@router.post("/usage")
def log_usage(
    usage_data: UsageLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log team member usage"""
    
    usage_log = UsageLog(**usage_data.model_dump())
    
    db.add(usage_log)
    db.commit()
    
    return {"message": "Usage logged successfully"}


@router.get("/analytics/usage-by-member")
def get_usage_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage analytics by team member"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    usage_stats = db.query(
        TeamMember.email,
        TeamMember.full_name,
        Subscription.service_name,
        func.count(UsageLog.id).label('usage_count'),
        func.sum(UsageLog.duration_minutes).label('total_minutes')
    ).join(
        UsageLog, UsageLog.team_member_id == TeamMember.id
    ).join(
        Subscription, Subscription.id == UsageLog.subscription_id
    ).filter(
        TeamMember.organization_id == current_user.id,
        UsageLog.usage_date >= cutoff_date
    ).group_by(
        TeamMember.email,
        TeamMember.full_name,
        Subscription.service_name
    ).all()
    
    return [
        {
            'email': stat[0],
            'name': stat[1],
            'service': stat[2],
            'usage_count': stat[3],
            'total_minutes': stat[4] or 0
        }
        for stat in usage_stats
    ]


@router.get("/shadow-it")
def get_shadow_it_detections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get shadow IT detections"""
    
    detections = db.query(ShadowITDetection).filter(
        ShadowITDetection.organization_id == current_user.id,
        ShadowITDetection.status == 'detected'
    ).all()
    
    return detections
