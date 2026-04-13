from fastapi import APIRouter
from .endpoints import (
    auth,
    users,
    subscriptions,
    analytics,
    recommendations,
    sms,
    summary,
    alternatives,
    emails,
    gmail,
    email_forward,
    team,
    negotiation,
    gamification
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(sms.router, prefix="/sms", tags=["sms"])
api_router.include_router(summary.router, prefix="/subscriptions", tags=["summary"])
api_router.include_router(alternatives.router, prefix="/subscriptions", tags=["alternatives"])
api_router.include_router(emails.router, prefix="/emails", tags=["email-intelligence"])
api_router.include_router(gmail.router, prefix="/gmail", tags=["gmail-integration"])
api_router.include_router(email_forward.router, prefix="/email-forward", tags=["email-forwarding"])
api_router.include_router(team.router, prefix="/team", tags=["team-tracking"])
api_router.include_router(negotiation.router, prefix="/negotiate", tags=["negotiation"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
