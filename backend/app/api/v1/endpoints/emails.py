"""Email intelligence endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ....db.base import get_db
from app.api.dependencies import get_current_user
from ....models import User
from ....models.email_receipt import EmailReceipt
from ....services.email_parser import EmailParser
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class ChromeExtensionReceipt(BaseModel):
    """Receipt data from Chrome extension"""
    messageId: str
    subject: str
    from_: str = None
    date: str
    vendor: str
    amount: Optional[float] = None
    snippet: str
    body: str


class BulkReceiptUpload(BaseModel):
    """Bulk upload from Chrome extension"""
    source: str  # 'gmail_extension'
    receipts: List[ChromeExtensionReceipt]
    scanned_at: str


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


@router.post("/upload")
def upload_receipts_from_extension(
    upload_data: BulkReceiptUpload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload receipts from Chrome extension
    
    This endpoint receives bulk receipt data from the Gmail Scanner Chrome extension
    and creates EmailReceipt records for tracking and analysis.
    """
    
    created_receipts = []
    updated_receipts = []
    skipped_receipts = []
    
    for receipt_data in upload_data.receipts:
        try:
            # Check if receipt already exists (by Gmail message ID)
            existing = db.query(EmailReceipt).filter(
                EmailReceipt.user_id == current_user.id,
                EmailReceipt.gmail_message_id == receipt_data.messageId
            ).first()
            
            if existing:
                # Update existing receipt if amount was found and didn't exist before
                if receipt_data.amount and not existing.amount:
                    existing.amount = receipt_data.amount
                    existing.vendor = receipt_data.vendor
                    existing.confidence_score = 0.8  # Chrome extension parsed it
                    existing.status = 'pending'
                    db.commit()
                    updated_receipts.append(existing.id)
                else:
                    skipped_receipts.append(receipt_data.messageId)
                continue
            
            # Parse received date
            try:
                received_date = datetime.fromisoformat(receipt_data.date.replace('Z', '+00:00'))
            except:
                received_date = datetime.utcnow()
            
            # Create new receipt
            new_receipt = EmailReceipt(
                user_id=current_user.id,
                gmail_message_id=receipt_data.messageId,
                email_subject=receipt_data.subject,
                sender_email=receipt_data.from_ or 'unknown@unknown.com',
                received_date=received_date,
                raw_body=receipt_data.body,
                vendor=receipt_data.vendor,
                amount=receipt_data.amount,
                currency='USD',  # Default, can be enhanced
                confidence_score=0.8 if receipt_data.amount else 0.5,
                is_subscription=True,  # Extension only scans subscription emails
                extracted_data={
                    'source': upload_data.source,
                    'snippet': receipt_data.snippet,
                    'scanned_at': upload_data.scanned_at
                },
                status='pending'
            )
            
            db.add(new_receipt)
            db.flush()  # Get ID without committing
            created_receipts.append(new_receipt.id)
            
        except Exception as e:
            print(f"Error processing receipt {receipt_data.messageId}: {str(e)}")
            skipped_receipts.append(receipt_data.messageId)
            continue
    
    # Commit all changes
    db.commit()
    
    return {
        "success": True,
        "message": f"Processed {len(upload_data.receipts)} receipts",
        "created": len(created_receipts),
        "updated": len(updated_receipts),
        "skipped": len(skipped_receipts),
        "receipt_ids": created_receipts,
        "total_receipts": len(created_receipts) + len(updated_receipts)
    }


@router.get("/stats")
def get_receipt_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics about email receipts"""
    
    total = db.query(EmailReceipt).filter(EmailReceipt.user_id == current_user.id).count()
    pending = db.query(EmailReceipt).filter(
        EmailReceipt.user_id == current_user.id,
        EmailReceipt.status == 'pending'
    ).count()
    matched = db.query(EmailReceipt).filter(
        EmailReceipt.user_id == current_user.id,
        EmailReceipt.status == 'matched'
    ).count()
    
    # Chrome extension scanned receipts
    extension_receipts = db.query(EmailReceipt).filter(
        EmailReceipt.user_id == current_user.id,
        EmailReceipt.gmail_message_id.isnot(None)
    ).count()
    
    # Total detected spending
    total_amount = db.query(func.sum(EmailReceipt.amount)).filter(
        EmailReceipt.user_id == current_user.id,
        EmailReceipt.amount.isnot(None)
    ).scalar() or 0
    
    return {
        "total_receipts": total,
        "pending": pending,
        "matched": matched,
        "from_extension": extension_receipts,
        "total_detected_spending": round(total_amount, 2)
    }
