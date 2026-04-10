"""Gamification and SaaS Score endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....db.base import get_db
from app.api.dependencies import get_current_user
from ....models import User
from ....models.gamification import SaaSScore, Achievement, UserAchievement, SavingsReport, ReferralLink
from ....services.scoring_engine import ScoringEngine
from pydantic import BaseModel
from datetime import datetime
import secrets

router = APIRouter()


class SaaSScoreResponse(BaseModel):
    score: int
    level: str
    rank_percentile: float | None
    total_savings: float
    subscriptions_tracked: int
    streak_days: int
    
    class Config:
        from_attributes = True


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    category: str | None
    points: int
    tier: str | None
    
    class Config:
        from_attributes = True


@router.get("/score", response_model=SaaSScoreResponse)
def get_saas_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's SaaS Score"""
    
    # Update score
    saas_score = ScoringEngine.update_score(db, current_user.id)
    
    return saas_score


@router.get("/achievements", response_model=List[AchievementResponse])
def get_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available achievements"""
    
    achievements = db.query(Achievement).filter(
        Achievement.is_active == True
    ).all()
    
    return achievements


@router.get("/achievements/unlocked")
def get_unlocked_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's unlocked achievements"""
    
    saas_score = db.query(SaaSScore).filter(
        SaaSScore.user_id == current_user.id
    ).first()
    
    if not saas_score:
        return []
    
    unlocked = db.query(UserAchievement, Achievement).join(
        Achievement
    ).filter(
        UserAchievement.score_id == saas_score.id
    ).all()
    
    return [
        {
            'achievement': ach,
            'unlocked_at': ua.unlocked_at,
            'progress': ua.progress
        }
        for ua, ach in unlocked
    ]


@router.post("/reports/generate")
def generate_savings_report(
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate shareable savings report"""
    
    from datetime import timedelta
    from ..models.subscription_alternative import SubscriptionAlternative
    
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=period_days)
    
    # Calculate savings
    alternatives = db.query(SubscriptionAlternative).join(
        SubscriptionAlternative.subscription
    ).filter(
        SubscriptionAlternative.subscription.has(user_id=current_user.id)
    ).all()
    
    total_saved = sum(alt.monthly_savings or 0 for alt in alternatives)
    
    # Generate report
    report = SavingsReport(
        user_id=current_user.id,
        report_type="monthly",
        period_start=period_start,
        period_end=period_end,
        total_saved=total_saved,
        subscriptions_optimized=len(alternatives),
        share_token=secrets.token_urlsafe(16),
        report_data={
            'alternatives': [
                {
                    'service': alt.subscription.service_name,
                    'savings': alt.monthly_savings
                }
                for alt in alternatives
            ]
        }
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        'report_id': report.id,
        'share_url': f"/reports/share/{report.share_token}",
        'total_saved': total_saved
    }


@router.get("/reports/share/{share_token}")
def view_shared_report(
    share_token: str,
    db: Session = Depends(get_db)
):
    """View shared savings report (public)"""
    
    report = db.query(SavingsReport).filter(
        SavingsReport.share_token == share_token
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Increment views
    report.views_count += 1
    db.commit()
    
    return report


@router.post("/referral/create")
def create_referral_link(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create referral link"""
    
    # Check for existing link
    existing = db.query(ReferralLink).filter(
        ReferralLink.user_id == current_user.id,
        ReferralLink.is_active == True
    ).first()
    
    if existing:
        return {
            'code': existing.code,
            'referral_url': f"/signup?ref={existing.code}"
        }
    
    # Create new link
    code = secrets.token_urlsafe(8)
    link = ReferralLink(
        user_id=current_user.id,
        code=code
    )
    
    db.add(link)
    db.commit()
    
    return {
        'code': code,
        'referral_url': f"/signup?ref={code}"
    }
