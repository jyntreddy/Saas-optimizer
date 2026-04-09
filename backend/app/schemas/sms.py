"""SMS Transaction Schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TwilioWebhook(BaseModel):
    """Schema for incoming Twilio webhook"""
    MessageSid: str
    From: str
    To: str
    Body: str
    AccountSid: Optional[str] = None
    NumMedia: Optional[str] = "0"


class SMSTransactionBase(BaseModel):
    """Base SMS Transaction schema"""
    vendor: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "USD"
    transaction_date: Optional[datetime] = None


class SMSTransactionCreate(SMSTransactionBase):
    """Create SMS Transaction schema"""
    from_number: str
    to_number: str
    message_sid: str
    raw_message: str
    subscription_id: Optional[int] = None
    matched: bool = False
    confidence_score: float = 0.0
    status: str = "pending"


class SMSTransactionUpdate(BaseModel):
    """Update SMS Transaction schema"""
    vendor: Optional[str] = None
    amount: Optional[float] = None
    subscription_id: Optional[int] = None
    matched: Optional[bool] = None
    status: Optional[str] = None


class SMSTransaction(SMSTransactionBase):
    """SMS Transaction response schema"""
    id: int
    user_id: int
    from_number: str
    to_number: str
    message_sid: str
    raw_message: str
    subscription_id: Optional[int] = None
    matched: bool
    confidence_score: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ParsedSMS(BaseModel):
    """Schema for parsed SMS data"""
    vendor: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "USD"
    transaction_date: Optional[datetime] = None
    confidence: float = 0.0
    raw_text: str
