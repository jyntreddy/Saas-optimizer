from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.subscription import SubscriptionStatus


class SubscriptionBase(BaseModel):
    service_name: str
    provider: Optional[str] = None
    cost: float
    billing_cycle: Optional[str] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    start_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    service_name: Optional[str] = None
    provider: Optional[str] = None
    cost: Optional[float] = None
    billing_cycle: Optional[str] = None
    status: Optional[SubscriptionStatus] = None
    renewal_date: Optional[datetime] = None


class SubscriptionInDB(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Subscription(SubscriptionInDB):
    pass
