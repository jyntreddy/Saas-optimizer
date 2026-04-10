"""SaaS Score calculation engine"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.gamification import SaaSScore


class ScoringEngine:
    """Calculate and update SaaS Score for users"""
    
    LEVEL_THRESHOLDS = {
        0: "Novice",
        100: "Explorer", 
        250: "Optimizer",
        500: "Expert",
        750: "Master",
        1000: "Legend"
    }
    
    @classmethod
    def calculate_score(cls, db: Session, user_id: int) -> int:
        """Calculate total SaaS Score"""
        from ..models import Subscription, User
        from ..models.negotiation import NegotiationSession
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0
        
        score = 0
        
        # Base points for tracking subscriptions (10 points each)
        sub_count = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).count()
        score += sub_count * 10
        
        # Points for total savings (1 point per $10 saved)
        total_savings = cls._calculate_total_savings(db, user_id)
        score += int(total_savings / 10)
        
        # Points for successful negotiations (50 points each)
        negotiation_wins = db.query(NegotiationSession).filter(
            NegotiationSession.user_id == user_id,
            NegotiationSession.status == "completed",
            NegotiationSession.achieved_price.isnot(None)
        ).count()
        score += negotiation_wins * 50
        
        # Streak bonus (5 points per day)
        saas_score = db.query(SaaSScore).filter(SaaSScore.user_id == user_id).first()
        if saas_score and saas_score.streak_days:
            score += saas_score.streak_days * 5
        
        # Referral bonus (20 points per referral)
        from ..models.gamification import ReferralLink
        referral_count = db.query(ReferralLink).filter(
            ReferralLink.user_id == user_id
        ).first()
        if referral_count:
            score += referral_count.conversions * 20
        
        return min(score, 1000)  # Cap at 1000
    
    @classmethod
    def get_level(cls, score: int) -> str:
        """Get level name from score"""
        for threshold in sorted(cls.LEVEL_THRESHOLDS.keys(), reverse=True):
            if score >= threshold:
                return cls.LEVEL_THRESHOLDS[threshold]
        return "Novice"
    
    @classmethod
    def update_score(cls, db: Session, user_id: int):
        """Update user's SaaS Score"""
        score_value = cls.calculate_score(db, user_id)
        level = cls.get_level(score_value)
        
        saas_score = db.query(SaaSScore).filter(SaaSScore.user_id == user_id).first()
        if not saas_score:
            saas_score = SaaSScore(user_id=user_id)
            db.add(saas_score)
        
        saas_score.score = score_value
        saas_score.level = level
        saas_score.last_activity = datetime.utcnow()
        
        # Update streak
        if saas_score.last_activity:
            days_diff = (datetime.utcnow() - saas_score.last_activity).days
            if days_diff == 1:
                saas_score.streak_days = (saas_score.streak_days or 0) + 1
            elif days_diff > 1:
                saas_score.streak_days = 1
        else:
            saas_score.streak_days = 1
        
        db.commit()
        db.refresh(saas_score)
        return saas_score
    
    @classmethod
    def _calculate_total_savings(cls, db: Session, user_id: int) -> float:
        """Calculate total savings from all optimizations"""
        from ..models.subscription_alternative import SubscriptionAlternative
        
        total = 0.0
        alternatives = db.query(SubscriptionAlternative).join(
            SubscriptionAlternative.subscription
        ).filter(
            SubscriptionAlternative.subscription.has(user_id=user_id)
        ).all()
        
        for alt in alternatives:
            if alt.monthly_savings:
                total += alt.monthly_savings
        
        return total
