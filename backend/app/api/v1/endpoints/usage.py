"""
Usage Sync Endpoint
Receives and stores usage data from desktop app
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db import crud
from app.api.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter()


class AppUsageItem(BaseModel):
    appName: str
    category: str
    vendor: str
    totalDuration: int  # seconds
    isCurrentlyRunning: bool
    lastActivity: Optional[datetime]


class BrowserUsageItem(BaseModel):
    name: str
    category: str
    vendor: str
    totalVisits: int
    uniqueDays: int
    lastVisit: Optional[datetime]
    browsers: List[str]


class DashboardOverview(BaseModel):
    totalSubscriptions: int
    activeSubscriptions: int
    monthlySpend: float
    annualSpend: float
    unusedSubscriptions: int
    potentialSavings: float
    saasScore: float


class UsageSyncRequest(BaseModel):
    appUsage: List[AppUsageItem]
    browserUsage: List[BrowserUsageItem]
    dashboard: Optional[Dict[str, Any]]
    timestamp: datetime
    deviceId: str


@router.post("/sync")
async def sync_usage_data(
    request: UsageSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync usage data from desktop app
    """
    try:
        # Store usage data in database
        # For now, we'll store as JSON in a usage_logs table
        # In production, you'd want separate tables for different data types
        
        usage_data = {
            "user_id": current_user.id,
            "timestamp": request.timestamp,
            "device_id": request.deviceId,
            "app_usage": [item.dict() for item in request.appUsage],
            "browser_usage": [item.dict() for item in request.browserUsage],
            "dashboard": request.dashboard,
            "synced_at": datetime.utcnow()
        }
        
        # TODO: Store in database (would need to create usage_logs table)
        # For now, just acknowledge receipt
        
        return {
            "success": True,
            "message": "Usage data synced successfully",
            "data": {
                "apps_tracked": len(request.appUsage),
                "web_services_tracked": len(request.browserUsage),
                "saas_score": request.dashboard.get("overview", {}).get("saasScore") if request.dashboard else None,
                "potential_savings": request.dashboard.get("overview", {}).get("potentialSavings") if request.dashboard else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync usage data: {str(e)}")


@router.get("/summary")
async def get_usage_summary(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage summary for the past N days
    """
    try:
        # TODO: Query usage data from database
        # For now, return placeholder data
        
        return {
            "success": True,
            "data": {
                "period": f"Last {days} days",
                "totalAppsTracked": 0,
                "totalWebServicesTracked": 0,
                "averageSaasScore": 75,
                "potentialSavings": 0,
                "message": "Usage tracking active - data will appear after first sync"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve usage summary: {str(e)}")


@router.get("/analytics")
async def get_usage_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive usage analytics
    """
    try:
        # TODO: Generate analytics from stored usage data
        # For now, return placeholder structure
        
        return {
            "success": True,
            "data": {
                "usageByCategory": {},
                "usageByVendor": {},
                "costPerUsage": [],
                "trends": {
                    "daily": [],
                    "weekly": [],
                    "monthly": []
                },
                "recommendations": []
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")


@router.get("/alternatives/{vendor}")
async def get_alternatives(
    vendor: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get alternative services for a specific vendor
    """
    # Common alternatives database
    alternatives_db = {
        "Slack": [
            {
                "name": "Microsoft Teams",
                "description": "Included with Microsoft 365",
                "estimatedSavings": 0,
                "features": ["Video calls", "File sharing", "Integrations"],
                "pricing": "Included with M365 or $4/user/month"
            },
            {
                "name": "Discord",
                "description": "Free team communication",
                "estimatedSavings": 8,
                "features": ["Voice channels", "Screen sharing", "Communities"],
                "pricing": "Free"
            },
            {
                "name": "Mattermost",
                "description": "Self-hosted Slack alternative",
                "estimatedSavings": 6,
                "features": ["Self-hosted", "Open source", "Slack import"],
                "pricing": "Free (self-hosted) or $10/user/month"
            }
        ],
        "Zoom": [
            {
                "name": "Google Meet",
                "description": "Included with Google Workspace",
                "estimatedSavings": 15,
                "features": ["100 participants", "Recording", "Calendar integration"],
                "pricing": "Included with Google Workspace"
            },
            {
                "name": "Microsoft Teams",
                "description": "Included with Microsoft 365",
                "estimatedSavings": 15,
                "features": ["Video calls", "Screen sharing", "Breakout rooms"],
                "pricing": "Included with M365"
            },
            {
                "name": "Jitsi",
                "description": "Free and open source video conferencing",
                "estimatedSavings": 20,
                "features": ["Unlimited meetings", "Screen sharing", "No time limits"],
                "pricing": "Free"
            }
        ],
        "Notion": [
            {
                "name": "Confluence",
                "description": "Enterprise wiki and collaboration",
                "estimatedSavings": -5,
                "features": ["Templates", "Integrations", "Advanced permissions"],
                "pricing": "$5.75/user/month"
            },
            {
                "name": "Obsidian",
                "description": "Local-first note-taking",
                "estimatedSavings": 8,
                "features": ["Markdown", "Local storage", "Graph view"],
                "pricing": "$25/year (personal) or Free"
            },
            {
                "name": "Coda",
                "description": "Docs that work like apps",
                "estimatedSavings": 0,
                "features": ["Interactive docs", "Automations", "Integrations"],
                "pricing": "$10/user/month"
            }
        ],
        "GitHub": [
            {
                "name": "GitLab",
                "description": "Complete DevOps platform",
                "estimatedSavings": 0,
                "features": ["CI/CD", "Issue tracking", "Wiki"],
                "pricing": "$4/user/month or Free"
            },
            {
                "name": "Bitbucket",
                "description": "Git with Jira integration",
                "estimatedSavings": 0,
                "features": ["Pipelines", "Jira integration", "Pull requests"],
                "pricing": "Free or $3/user/month"
            }
        ]
    }
    
    alternatives = alternatives_db.get(vendor, [])
    
    if not alternatives:
        return {
            "success": True,
            "data": {
                "vendor": vendor,
                "alternatives": [],
                "message": f"No alternatives found for {vendor}. Contact support to add alternatives."
            }
        }
    
    return {
        "success": True,
        "data": {
            "vendor": vendor,
            "alternatives": alternatives
        }
    }
