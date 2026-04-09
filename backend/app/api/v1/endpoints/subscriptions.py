from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ....db.base import get_db
from ....schemas import subscription as schemas
from ....models.subscription import Subscription

router = APIRouter()


@router.get("/", response_model=List[schemas.Subscription])
def list_subscriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all subscriptions for current user"""
    # TODO: Add authentication and filter by current user
    subscriptions = db.query(Subscription).offset(skip).limit(limit).all()
    return subscriptions


@router.post("/", response_model=schemas.Subscription, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription_in: schemas.SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create new subscription"""
    # TODO: Get user_id from authenticated user
    user_id = 1  # Placeholder
    
    db_subscription = Subscription(
        **subscription_in.dict(),
        user_id=user_id
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.get("/{subscription_id}", response_model=schemas.Subscription)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Get subscription by ID"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.put("/{subscription_id}", response_model=schemas.Subscription)
def update_subscription(
    subscription_id: int,
    subscription_in: schemas.SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """Update subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    update_data = subscription_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    db.commit()
    db.refresh(subscription)
    return subscription


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Delete subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(subscription)
    db.commit()
    return None
