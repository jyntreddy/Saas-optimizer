"""Database CRUD operations for subscriptions"""

from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.subscription import Subscription, SubscriptionStatus
from ..schemas.subscription import SubscriptionCreate, SubscriptionUpdate


def get_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
    """Get subscription by ID"""
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def get_subscriptions(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Subscription]:
    """Get all subscriptions for a user"""
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_active_subscriptions(db: Session, user_id: int) -> List[Subscription]:
    """Get active subscriptions for a user"""
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
        .all()
    )


def create_subscription(
    db: Session, 
    subscription: SubscriptionCreate, 
    user_id: int
) -> Subscription:
    """Create new subscription"""
    db_subscription = Subscription(**subscription.dict(), user_id=user_id)
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def update_subscription(
    db: Session,
    subscription_id: int,
    subscription_update: SubscriptionUpdate
) -> Optional[Subscription]:
    """Update subscription"""
    db_subscription = get_subscription(db, subscription_id)
    if not db_subscription:
        return None
    
    update_data = subscription_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subscription, field, value)
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def delete_subscription(db: Session, subscription_id: int) -> bool:
    """Delete subscription"""
    db_subscription = get_subscription(db, subscription_id)
    if not db_subscription:
        return False
    
    db.delete(db_subscription)
    db.commit()
    return True
