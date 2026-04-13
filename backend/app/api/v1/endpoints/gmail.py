"""Gmail API Integration Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
import secrets

from ....db.base import get_db
from ....models.user import User
from ....models.gmail_token import GmailToken
from ....api.dependencies import get_current_user
from ....services.gmail_service import GmailService
from ....core.config import settings

router = APIRouter()


class GmailAuthResponse(BaseModel):
    auth_url: str
    state: str


class GmailCallbackRequest(BaseModel):
    code: str
    state: str


class GmailScanRequest(BaseModel):
    max_results: int = 50
    query: str = "label:receipts OR subject:(receipt OR invoice OR subscription OR payment)"


@router.get("/auth-url", response_model=GmailAuthResponse)
def get_gmail_auth_url(
    current_user: User = Depends(get_current_user)
):
    """Get Gmail OAuth authorization URL"""
    
    if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Gmail OAuth not configured. Please set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET"
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state temporarily (in production, use Redis)
    # For now, we'll validate in callback
    
    auth_url = GmailService.get_auth_url(
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        redirect_uri=settings.GMAIL_REDIRECT_URI,
        state=state
    )
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/callback")
def gmail_oauth_callback(
    callback_data: GmailCallbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Handle Gmail OAuth callback"""
    
    try:
        # Exchange code for tokens
        token_data = GmailService.exchange_code_for_token(
            code=callback_data.code,
            client_id=settings.GMAIL_CLIENT_ID,
            client_secret=settings.GMAIL_CLIENT_SECRET,
            redirect_uri=settings.GMAIL_REDIRECT_URI
        )
        
        # Check if token already exists
        gmail_token = db.query(GmailToken).filter(
            GmailToken.user_id == current_user.id
        ).first()
        
        if gmail_token:
            # Update existing
            gmail_token.access_token = token_data['access_token']
            gmail_token.refresh_token = token_data['refresh_token']
            gmail_token.token_uri = token_data['token_uri']
            gmail_token.client_id = token_data['client_id']
            gmail_token.client_secret = token_data['client_secret']
            gmail_token.scopes = str(token_data['scopes'])
            gmail_token.expires_at = token_data['expires_at']
            gmail_token.is_active = True
        else:
            # Create new
            gmail_token = GmailToken(
                user_id=current_user.id,
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=str(token_data['scopes']),
                expires_at=token_data['expires_at'],
                is_active=True
            )
            db.add(gmail_token)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Gmail connected successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.post("/scan")
def scan_gmail_receipts(
    scan_request: GmailScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scan Gmail for receipt emails"""
    
    result = GmailService.scan_emails(
        db=db,
        user=current_user,
        max_results=scan_request.max_results,
        query=scan_request.query
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/status")
def get_gmail_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check Gmail connection status"""
    
    gmail_token = db.query(GmailToken).filter(
        GmailToken.user_id == current_user.id,
        GmailToken.is_active == True
    ).first()
    
    if not gmail_token:
        return {
            "connected": False,
            "last_synced": None
        }
    
    return {
        "connected": True,
        "last_synced": gmail_token.last_synced_at,
        "watched_labels": gmail_token.watched_labels
    }


@router.post("/disconnect")
def disconnect_gmail(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect Gmail integration"""
    
    success = GmailService.disconnect(db, current_user)
    
    if not success:
        raise HTTPException(status_code=404, detail="Gmail not connected")
    
    return {
        "success": True,
        "message": "Gmail disconnected successfully"
    }
