"""SMS Transaction Endpoint - Desktop App Integration"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import hashlib

from app.db.base import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.sms_transaction import SMSTransaction
from app.schemas.sms import (
    SMSTransactionCreate,
    SMSTransactionUpload,
    SMSTransaction as SMSTransactionSchema,
    ParsedSMS
)
from app.services.sms_parser import SMSParser
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/upload", response_model=SMSTransactionSchema)
async def upload_sms(
    sms_data: SMSTransactionUpload,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SMSTransaction:
    """
    Upload SMS from desktop app
    
    The desktop app scans local SMS databases and uploads transactions
    """
    
    # Parse the SMS
    parsed = SMSParser.parse(sms_data.message)
    
    if not SMSParser.is_subscription_sms(sms_data.message):
        raise HTTPException(status_code=400, detail="Not a subscription-related SMS")
    
    # Generate unique message ID from content hash
    message_hash = hashlib.sha256(
        f"{sms_data.sender}{sms_data.message}{sms_data.timestamp}".encode()
    ).hexdigest()[:32]
    
    # Check if message already processed
    existing = db.query(SMSTransaction).filter(
        SMSTransaction.message_sid == message_hash
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="SMS already processed")
    
    # Create SMS transaction
    sms_transaction = SMSTransaction(
        user_id=current_user.id,
        from_number=sms_data.sender,
        to_number=sms_data.recipient or "desktop-app",
        message_sid=message_hash,
        raw_message=sms_data.message,
        vendor=parsed.vendor,
        amount=parsed.amount,
        currency=parsed.currency,
        transaction_date=sms_data.timestamp or parsed.transaction_date,
        confidence_score=parsed.confidence,
        status="pending"
    )
    
    # Try to match with existing subscription
    if parsed.vendor and parsed.amount:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.service_name.ilike(f"%{parsed.vendor}%")
        ).first()
        
        if subscription:
            sms_transaction.subscription_id = subscription.id
            sms_transaction.matched = True
            sms_transaction.status = "matched"
    
    db.add(sms_transaction)
    db.commit()
    db.refresh(sms_transaction)
    
    return sms_transaction


@router.post("/parse", response_model=ParsedSMS)
async def parse_sms(
    message: str,
    current_user: User = Depends(get_current_user)
) -> ParsedSMS:
    """
    Parse SMS message manually (for testing)
    """
    return SMSParser.parse(message)


@router.get("/transactions", response_model=list[SMSTransactionSchema])
async def get_sms_transactions(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[SMSTransaction]:
    """
    Get SMS transactions for current user
    """
    query = db.query(SMSTransaction).filter(SMSTransaction.user_id == current_user.id)
    
    if status:
        query = query.filter(SMSTransaction.status == status)
    
    transactions = query.order_by(SMSTransaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions


@router.patch("/transactions/{transaction_id}/status")
async def update_transaction_status(
    transaction_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update SMS transaction status (confirmed/ignored)
    """
    transaction = db.query(SMSTransaction).filter(
        SMSTransaction.id == transaction_id,
        SMSTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if status not in ["pending", "confirmed", "ignored", "matched"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    transaction.status = status
    db.commit()
    
    return {"status": "success", "transaction_id": transaction_id, "new_status": status}


@router.post("/transactions/{transaction_id}/create-subscription")
async def create_subscription_from_sms(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a subscription from an SMS transaction
    """
    transaction = db.query(SMSTransaction).filter(
        SMSTransaction.id == transaction_id,
        SMSTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if not transaction.vendor or not transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient data to create subscription")
    
    # Check if subscription already exists
    if transaction.subscription_id:
        return {
            "status": "exists",
            "subscription_id": transaction.subscription_id,
            "message": "Subscription already linked"
        }
    
    # Create new subscription
    subscription = Subscription(
        user_id=current_user.id,
        service_name=transaction.vendor,
        cost=transaction.amount,
        currency=transaction.currency,
        billing_cycle="monthly",  # Default
        status="active",
        provider=transaction.vendor
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Link transaction to subscription
    transaction.subscription_id = subscription.id
    transaction.matched = True
    transaction.status = "confirmed"
    db.commit()
    
    return {
        "status": "created",
        "subscription_id": subscription.id,
        "message": "Subscription created successfully"
    }
