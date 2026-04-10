"""Negotiation bot endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....db.base import get_db
from app.api.dependencies import get_current_user
from ....models import User, Subscription
from ....models.negotiation import NegotiationSession, PriceIntelligence
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class NegotiationCreate(BaseModel):
    subscription_id: int
    target_price: float | None = None


class PriceIntelSubmit(BaseModel):
    vendor: str
    plan_name: str | None = None
    reported_price: float
    billing_cycle: str | None = None
    company_size: str | None = None
    negotiated_discount: float | None = None


class NegotiationResponse(BaseModel):
    id: int
    vendor: str
    current_price: float
    target_price: float | None
    status: str
    started_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/sessions", response_model=NegotiationResponse)
def start_negotiation(
    nego_data: NegotiationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a negotiation session"""
    
    subscription = db.query(Subscription).filter(
        Subscription.id == nego_data.subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Calculate target price (aim for 20% discount if not specified)
    target = nego_data.target_price or (subscription.cost * 0.8)
    
    session = NegotiationSession(
        user_id=current_user.id,
        subscription_id=subscription.id,
        vendor=subscription.service_name,
        current_price=subscription.cost,
        target_price=target,
        status="initiated",
        strategy="standard_discount_request"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions", response_model=List[NegotiationResponse])
def get_negotiations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all negotiation sessions"""
    
    sessions = db.query(NegotiationSession).filter(
        NegotiationSession.user_id == current_user.id
    ).all()
    
    return sessions


@router.patch("/sessions/{session_id}/complete")
def complete_negotiation(
    session_id: int,
    achieved_price: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark negotiation as completed"""
    
    session = db.query(NegotiationSession).filter(
        NegotiationSession.id == session_id,
        NegotiationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.achieved_price = achieved_price
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    
    # Update subscription cost
    if session.subscription:
        session.subscription.cost = achieved_price
    
    db.commit()
    
    return {"message": "Negotiation completed", "savings": session.current_price - achieved_price}


@router.post("/price-intel")
def submit_price_intel(
    price_data: PriceIntelSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit price intelligence"""
    
    intel = PriceIntelligence(
        vendor=price_data.vendor,
        plan_name=price_data.plan_name,
        reported_price=price_data.reported_price,
        billing_cycle=price_data.billing_cycle,
        company_size=price_data.company_size,
        negotiated_discount=price_data.negotiated_discount,
        submitted_by=current_user.id,
        verification_status='pending'
    )
    
    db.add(intel)
    db.commit()
    
    return {"message": "Price intel submitted successfully"}


@router.get("/price-intel/{vendor}")
def get_price_intel(
    vendor: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price intelligence for a vendor"""
    
    intel = db.query(PriceIntelligence).filter(
        PriceIntelligence.vendor.ilike(f"%{vendor}%"),
        PriceIntelligence.verification_status == 'verified'
    ).all()
    
    return intel
