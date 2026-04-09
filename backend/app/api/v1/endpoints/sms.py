"""SMS Webhook Endpoint"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.base import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.sms_transaction import SMSTransaction
from app.schemas.sms import (
    TwilioWebhook,
    SMSTransactionCreate,
    SMSTransaction as SMSTransactionSchema,
    ParsedSMS
)
from app.services.sms_parser import SMSParser
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/webhook", status_code=200)
async def receive_twilio_webhook(
    background_tasks: BackgroundTasks,
    MessageSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    AccountSid: str = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Receive SMS webhook from Twilio
    
    Twilio sends form-encoded data, not JSON
    """
    
    # Parse the SMS
    parsed = SMSParser.parse(Body)
    
    if not SMSParser.is_subscription_sms(Body):
        return {"status": "ignored", "reason": "Not a subscription SMS"}
    
    # Find user by phone number (To number)
    # In production, you'd have a phone number -> user mapping
    user = db.query(User).filter(User.is_active == True).first()
    
    if not user:
        return {"status": "error", "reason": "User not found"}
    
    # Check if message already processed
    existing = db.query(SMSTransaction).filter(
        SMSTransaction.message_sid == MessageSid
    ).first()
    
    if existing:
        return {"status": "duplicate", "reason": "Message already processed"}
    
    # Create SMS transaction
    sms_transaction = SMSTransaction(
        user_id=user.id,
        from_number=From,
        to_number=To,
        message_sid=MessageSid,
        raw_message=Body,
        vendor=parsed.vendor,
        amount=parsed.amount,
        currency=parsed.currency,
        transaction_date=parsed.transaction_date,
        confidence_score=parsed.confidence,
        status="pending"
    )
    
    # Try to match with existing subscription
    if parsed.vendor and parsed.amount:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.service_name.ilike(f"%{parsed.vendor}%")
        ).first()
        
        if subscription:
            sms_transaction.subscription_id = subscription.id
            sms_transaction.matched = True
            sms_transaction.status = "matched"
    
    db.add(sms_transaction)
    db.commit()
    db.refresh(sms_transaction)
    
    return {
        "status": "success",
        "message": "SMS processed",
        "transaction_id": str(sms_transaction.id),
        "parsed_vendor": parsed.vendor or "unknown",
        "parsed_amount": str(parsed.amount) if parsed.amount else "unknown"
    }


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
