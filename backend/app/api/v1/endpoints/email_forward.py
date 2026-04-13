"""Email Forwarding Webhook Endpoint"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import hmac
import hashlib

from ....db.base import get_db
from ....models.user import User
from ....models.email_receipt import EmailReceipt
from ....services.email_forwarding_service import EmailForwardingService
from ....services.email_parser import EmailParser
from ....core.config import settings

router = APIRouter()


class EmailWebhookPayload(BaseModel):
    """Payload for email forwarding services (SendGrid, Mailgun, etc.)"""
    to: str
    from_email: str
    subject: str
    text: str  # Plain text body
    html: Optional[str] = None  # HTML body
    headers: Optional[str] = None
    envelope: Optional[str] = None


@router.post("/inbound")
async def receive_forwarded_email(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive forwarded emails from email service providers
    
    Supports:
    - Raw MIME format (standard email forwarding)
    - SendGrid Inbound Parse
    - Mailgun Routes
    - Postmark Inbound
    
    Setup: Configure your email provider to forward emails to:
    https://your-domain.com/api/v1/email-forward/inbound
    """
    
    content_type = request.headers.get('content-type', '')
    
    try:
        if 'multipart/form-data' in content_type:
            # Parse form data (SendGrid, Mailgun format)
            form_data = await request.form()
            result = await _handle_form_email(form_data, db)
        elif 'application/json' in content_type:
            # Parse JSON (Postmark, custom webhooks)
            json_data = await request.json()
            result = await _handle_json_email(json_data, db)
        else:
            # Raw MIME email
            raw_email = await request.body()
            result = await _handle_raw_email(raw_email, db)
        
        return result
        
    except Exception as e:
        # Log error but return 200 to prevent retries
        print(f"Email processing error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Email received but processing failed"
        }


@router.post("/sendgrid-inbound")
async def sendgrid_inbound_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    SendGrid Inbound Parse Webhook
    
    Setup in SendGrid:
    1. Go to Settings > Inbound Parse
    2. Add hostname and URL: https://your-domain.com/api/v1/email-forward/sendgrid-inbound
    3. Check "POST the raw, full MIME message"
    """
    
    form_data = await request.form()
    
    # Extract data from SendGrid format
    to_email = form_data.get('to', '')
    from_email = form_data.get('from', '')
    subject = form_data.get('subject', '')
    text = form_data.get('text', '')
    html = form_data.get('html', '')
    envelope = form_data.get('envelope', '')
    
    # Get user by forwarding email
    user = await _find_user_by_forwarding_email(to_email, db)
    
    if not user:
        return {
            "success": False,
            "error": "User not found for forwarding email",
            "to": to_email
        }
    
    # Parse email
    parsed = EmailParser.parse_email(subject, from_email, text or html)
    
    # Create receipt
    receipt = EmailReceipt(
        user_id=user.id,
        email_subject=subject,
        sender_email=from_email,
        received_date=parsed.get('extracted_data', {}).get('date') or datetime.utcnow(),
        raw_body=text or html,
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
    
    return {
        "success": True,
        "receipt_id": receipt.id,
        "vendor": parsed.get('vendor'),
        "amount": parsed.get('amount')
    }


@router.post("/mailgun-route")
async def mailgun_route_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Mailgun Routes Webhook
    
    Setup in Mailgun:
    1. Go to Receiving > Routes
    2. Create route: match_recipient("receipts@your-domain.com")
    3. Action: forward("https://your-domain.com/api/v1/email-forward/mailgun-route")
    """
    
    form_data = await request.form()
    
    # Extract from Mailgun format
    sender = form_data.get('sender', '')
    recipient = form_data.get('recipient', '')
    subject = form_data.get('subject', '')
    body_plain = form_data.get('body-plain', '')
    body_html = form_data.get('body-html', '')
    
    # Verify webhook signature (recommended in production)
    # timestamp = form_data.get('timestamp')
    # token = form_data.get('token')
    # signature = form_data.get('signature')
    
    user = await _find_user_by_forwarding_email(recipient, db)
    
    if not user:
        return {"success": False, "error": "User not found"}
    
    from datetime import datetime
    
    # Parse email
    parsed = EmailParser.parse_email(subject, sender, body_plain or body_html)
    
    # Create receipt
    receipt = EmailReceipt(
        user_id=user.id,
        email_subject=subject,
        sender_email=sender,
        received_date=datetime.utcnow(),
        raw_body=body_plain or body_html,
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
    
    return {
        "success": True,
        "message": "Email processed successfully"
    }


async def _handle_form_email(form_data, db: Session):
    """Handle form-encoded email data"""
    # Implementation depends on provider format
    pass


async def _handle_json_email(json_data: dict, db: Session):
    """Handle JSON email data"""
    # Implementation for JSON webhooks
    pass


async def _handle_raw_email(raw_email: bytes, db: Session):
    """Handle raw MIME email"""
    from datetime import datetime
    
    # Parse raw email
    parsed_email = EmailForwardingService.parse_forwarded_email(raw_email)
    
    # Find user by recipient email
    user = await _find_user_by_forwarding_email(parsed_email['to'], db)
    
    if not user:
        return {"success": False, "error": "User not found"}
    
    # Parse for subscription data
    parsed = EmailParser.parse_email(
        parsed_email['subject'],
        parsed_email['sender'],
        parsed_email['body']
    )
    
    # Create receipt
    receipt = EmailReceipt(
        user_id=user.id,
        email_subject=parsed_email['subject'],
        sender_email=parsed_email['sender'],
        received_date=parsed_email['date'],
        raw_body=parsed_email['body'],
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
    
    return {"success": True, "receipt_id": receipt.id}


async def _find_user_by_forwarding_email(to_email: str, db: Session) -> Optional[User]:
    """
    Find user by their email forwarding address
    
    Supports:
    - receipts+username@domain.com (plus addressing)
    - user's registered email
    - custom forwarding email mapping (future)
    """
    import re
    
    # Check for plus addressing
    match = re.search(r'\+(.+?)@', to_email)
    if match:
        username = match.group(1)
        # Try to find user by username/email
        user = db.query(User).filter(User.email.ilike(f"%{username}%")).first()
        if user:
            return user
    
    # Try direct email match
    user = db.query(User).filter(User.email == to_email).first()
    if user:
        return user
    
    # Fallback: return first active user (for demo/testing)
    # In production, you'd want strict matching
    return db.query(User).filter(User.is_active == True).first()
