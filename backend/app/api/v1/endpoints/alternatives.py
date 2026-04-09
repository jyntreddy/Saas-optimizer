"""Subscription Alternatives Endpoint"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.base import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.subscription_alternative import SubscriptionAlternative
from app.schemas.alternatives import (
    SubscriptionAlternative as AlternativeSchema,
    AlternativeSuggestion
)
from app.api.dependencies import get_current_user

router = APIRouter()


# Alternative plans database (in production, this would be a separate table/API)
ALTERNATIVE_PLANS = {
    "netflix": [
        {"name": "Netflix Basic", "provider": "Netflix", "cost": 6.99, "features": "720p, 1 screen"},
        {"name": "Hulu (Ad-supported)", "provider": "Hulu", "cost": 7.99, "features": "Ads, HD streaming"},
        {"name": "Disney+ Basic", "provider": "Disney", "cost": 7.99, "features": "HD streaming, Disney content"},
    ],
    "spotify": [
        {"name": "Spotify Free", "provider": "Spotify", "cost": 0.00, "features": "Ads, shuffle only"},
        {"name": "YouTube Music Premium", "provider": "Google", "cost": 10.99, "features": "Ad-free, downloads"},
        {"name": "Apple Music Student", "provider": "Apple", "cost": 5.99, "features": "Full library, student discount"},
    ],
    "dropbox": [
        {"name": "Google Drive", "provider": "Google", "cost": 1.99, "features": "100GB storage"},
        {"name": "OneDrive", "provider": "Microsoft", "cost": 1.99, "features": "100GB storage, Office integration"},
        {"name": "iCloud+", "provider": "Apple", "cost": 0.99, "features": "50GB storage"},
    ],
    "adobe": [
        {"name": "Canva Pro", "provider": "Canva", "cost": 12.99, "features": "Design tools, templates"},
        {"name": "Affinity Designer", "provider": "Serif", "cost": 54.99, "features": "One-time purchase, professional tools"},
        {"name": "Adobe Photography Plan", "provider": "Adobe", "cost": 9.99, "features": "Photoshop + Lightroom only"},
    ],
    "zoom": [
        {"name": "Google Meet", "provider": "Google", "cost": 0.00, "features": "Free up to 60 min"},
        {"name": "Microsoft Teams", "provider": "Microsoft", "cost": 0.00, "features": "Free basic plan"},
        {"name": "Zoom Basic", "provider": "Zoom", "cost": 0.00, "features": "Free up to 40 min"},
    ],
}


@router.get("/alternatives", response_model=List[AlternativeSuggestion])
async def get_subscription_alternatives(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[AlternativeSuggestion]:
    """
    Get alternative subscription suggestions for all user subscriptions
    
    Returns cheaper plans or competitor alternatives with potential savings
    """
    
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).all()
    
    suggestions = []
    
    for sub in subscriptions:
        alternatives = _find_alternatives(sub, db)
        
        if alternatives:
            # Calculate total potential savings
            current_monthly_cost = sub.cost if sub.billing_cycle == "monthly" else sub.cost / 12
            total_savings = sum(alt.monthly_savings or 0 for alt in alternatives if alt.monthly_savings)
            
            # Find best alternative (highest savings)
            best_alt = max(alternatives, key=lambda x: x.monthly_savings or 0) if alternatives else None
            
            suggestions.append(AlternativeSuggestion(
                subscription_id=sub.id,
                subscription_name=sub.service_name,
                current_cost=current_monthly_cost,
                billing_cycle=sub.billing_cycle,
                alternatives=alternatives,
                total_potential_savings=total_savings,
                best_alternative=best_alt
            ))
    
    return suggestions


@router.get("/alternatives/{subscription_id}", response_model=AlternativeSuggestion)
async def get_alternatives_for_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AlternativeSuggestion:
    """
    Get alternative suggestions for a specific subscription
    """
    
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    alternatives = _find_alternatives(subscription, db)
    current_monthly_cost = subscription.cost if subscription.billing_cycle == "monthly" else subscription.cost / 12
    total_savings = sum(alt.monthly_savings or 0 for alt in alternatives if alt.monthly_savings)
    best_alt = max(alternatives, key=lambda x: x.monthly_savings or 0) if alternatives else None
    
    return AlternativeSuggestion(
        subscription_id=subscription.id,
        subscription_name=subscription.service_name,
        current_cost=current_monthly_cost,
        billing_cycle=subscription.billing_cycle,
        alternatives=alternatives,
        total_potential_savings=total_savings,
        best_alternative=best_alt
    )


@router.post("/alternatives/{subscription_id}/generate")
async def generate_alternatives(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate and store alternative suggestions for a subscription
    """
    
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Delete existing alternatives
    db.query(SubscriptionAlternative).filter(
        SubscriptionAlternative.subscription_id == subscription_id
    ).delete()
    
    # Generate new alternatives
    alternatives = _find_alternatives(subscription, db, store=True)
    
    return {
        "status": "success",
        "subscription_id": subscription_id,
        "alternatives_count": len(alternatives),
        "alternatives": [
            {
                "id": alt.id,
                "name": alt.alternative_name,
                "cost": alt.alternative_cost,
                "savings": alt.monthly_savings
            }
            for alt in alternatives
        ]
    }


def _find_alternatives(
    subscription: Subscription,
    db: Session,
    store: bool = False
) -> List[AlternativeSchema]:
    """
    Find alternative plans for a subscription
    
    Args:
        subscription: The subscription to find alternatives for
        db: Database session
        store: Whether to store alternatives in database
        
    Returns:
        List of alternative subscription schemas
    """
    
    service_name_lower = subscription.service_name.lower()
    current_monthly_cost = subscription.cost if subscription.billing_cycle == "monthly" else subscription.cost / 12
    
    # Check if we have alternatives in our database
    alternatives_list = []
    
    # Find matching alternatives from our plans database
    for key, plans in ALTERNATIVE_PLANS.items():
        if key in service_name_lower:
            for plan in plans:
                monthly_savings = current_monthly_cost - plan["cost"]
                annual_savings = monthly_savings * 12
                savings_percentage = (monthly_savings / current_monthly_cost * 100) if current_monthly_cost > 0 else 0
                
                # Only include if there are savings
                if monthly_savings > 0:
                    alt_data = {
                        "subscription_id": subscription.id,
                        "alternative_name": plan["name"],
                        "alternative_provider": plan["provider"],
                        "alternative_cost": plan["cost"],
                        "billing_cycle": "monthly",
                        "monthly_savings": round(monthly_savings, 2),
                        "annual_savings": round(annual_savings, 2),
                        "savings_percentage": round(savings_percentage, 2),
                        "reason": f"Save ${monthly_savings:.2f}/month by switching to {plan['name']}",
                        "features_comparison": plan["features"],
                        "recommendation_score": min(savings_percentage / 10, 10.0)
                    }
                    
                    if store:
                        # Store in database
                        alt = SubscriptionAlternative(**alt_data)
                        db.add(alt)
                        db.commit()
                        db.refresh(alt)
                        alternatives_list.append(AlternativeSchema.from_orm(alt))
                    else:
                        # Return as schema
                        alternatives_list.append(AlternativeSchema(**alt_data))
            
            break  # Found matching service
    
    # If no alternatives found, suggest generic money-saving tips
    if not alternatives_list:
        generic_alt = {
            "subscription_id": subscription.id,
            "alternative_name": f"{subscription.service_name} - Lower Tier",
            "alternative_provider": subscription.provider or subscription.service_name,
            "alternative_cost": current_monthly_cost * 0.7,  # Assume 30% cheaper tier
            "billing_cycle": "monthly",
            "monthly_savings": round(current_monthly_cost * 0.3, 2),
            "annual_savings": round(current_monthly_cost * 0.3 * 12, 2),
            "savings_percentage": 30.0,
            "reason": "Consider downgrading to a basic/lower tier plan",
            "features_comparison": "Basic features at lower cost",
            "recommendation_score": 5.0
        }
        
        if store:
            alt = SubscriptionAlternative(**generic_alt)
            db.add(alt)
            db.commit()
            db.refresh(alt)
            alternatives_list.append(AlternativeSchema.from_orm(alt))
        else:
            alternatives_list.append(AlternativeSchema(**generic_alt))
    
    return alternatives_list
