"""Email intelligence endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....db.base import get_db
from app.api.dependencies import get_current_user
from ....models import User
from ....models.email_receipt import EmailReceipt
from ....services.email_parser import EmailParser
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class EmailReceiptCreate(BaseModel):
    email_subject: str
    sender_email: str
    raw_body: str
    received_date: datetime


class EmailReceiptResponse(BaseModel):
    id: int
    vendor: str | None
    amount: float | None
    category: str | None
    confidence_score: float | None
    is_subscription: bool
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/scan", response_model=EmailReceiptResponse)
def scan_email_receipt(
    email_data: EmailReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scan and parse an email receipt"""
    
    # Parse email
    parsed = EmailParser.parse_email(
        email_data.email_subject,
        email_data.sender_email,
        email_data.raw_body
    )
    
    # Create receipt record
    receipt = EmailReceipt(
        user_id=current_user.id,
        email_subject=email_data.email_subject,
        sender_email=email_data.sender_email,
        received_date=email_data.received_date,
        raw_body=email_data.raw_body,
        vendor=parsed.get('vendor'),
        amount=parsed.get('amount'),
        currency=parsed.get('currency'),
        category=parsed.get('category'),
        confidence_score=parsed.get('confidence_score'),
        is_subscription=parsed.get('is_subscription', False),
        extracted_data=parsed.get('extracted_data'),
        status='pending'
    )
    
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    
    return receipt


@router.get("/receipts", response_model=List[EmailReceiptResponse])
def get_email_receipts(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all email receipts for current user"""
    
    query = db.query(EmailReceipt).filter(EmailReceipt.user_id == current_user.id)
    
    if status:
        query = query.filter(EmailReceipt.status == status)
    
    receipts = query.offset(skip).limit(limit).all()
    return receipts


@router.patch("/receipts/{receipt_id}/status")
def update_receipt_status(
    receipt_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update email receipt status"""
    
    receipt = db.query(EmailReceipt).filter(
        EmailReceipt.id == receipt_id,
        EmailReceipt.user_id == current_user.id
    ).first()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    receipt.status = status
    if status in ['matched', 'processed']:
        receipt.processed_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Status updated successfully"}
