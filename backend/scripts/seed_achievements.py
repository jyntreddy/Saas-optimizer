"""Seed default achievements"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.gamification import Achievement

def seed_achievements():
    db = SessionLocal()
    
    # Check if already seeded
    existing = db.query(Achievement).first()
    if existing:
        print("Achievements already seeded")
        return
    
    achievements = [
        # Common tier
        {
            "name": "First Steps",
            "description": "Track your first subscription",
            "icon": "🎯",
            "category": "onboarding",
            "points": 10,
            "tier": "common",
            "requirement_type": "subscriptions_tracked",
            "requirement_value": 1
        },
        {
            "name": "Budget Aware",
            "description": "Track 5 subscriptions",
            "icon": "📊",
            "category": "tracking",
            "points": 25,
            "tier": "common",
            "requirement_type": "subscriptions_tracked",
            "requirement_value": 5
        },
        {
            "name": "First Save",
            "description": "Save your first $10",
            "icon": "💰",
            "category": "savings",
            "points": 15,
            "tier": "common",
            "requirement_type": "total_savings",
            "requirement_value": 10
        },
        
        # Rare tier
        {
            "name": "Duplicate Detective",
            "description": "Find 3 duplicate subscriptions",
            "icon": "🔍",
            "category": "optimization",
            "points": 50,
            "tier": "rare",
            "requirement_type": "duplicates_found",
            "requirement_value": 3
        },
        {
            "name": "Negotiation Novice",
            "description": "Win your first negotiation",
            "icon": "💼",
            "category": "negotiation",
            "points": 50,
            "tier": "rare",
            "requirement_type": "negotiations_won",
            "requirement_value": 1
        },
        {
            "name": "Hundred Saver",
            "description": "Save $100 total",
            "icon": "💵",
            "category": "savings",
            "points": 75,
            "tier": "rare",
            "requirement_type": "total_savings",
            "requirement_value": 100
        },
        
        # Epic tier
        {
            "name": "Power User",
            "description": "Track 20+ subscriptions",
            "icon": "⚡",
            "category": "tracking",
            "points": 100,
            "tier": "epic",
            "requirement_type": "subscriptions_tracked",
            "requirement_value": 20
        },
        {
            "name": "Negotiation Pro",
            "description": "Win 5 negotiations",
            "icon": "🏆",
            "category": "negotiation",
            "points": 150,
            "tier": "epic",
            "requirement_type": "negotiations_won",
            "requirement_value": 5
        },
        {
            "name": "Grand Saver",
            "description": "Save $500 total",
            "icon": "💎",
            "category": "savings",
            "points": 200,
            "tier": "epic",
            "requirement_type": "total_savings",
            "requirement_value": 500
        },
        
        # Legendary tier
        {
            "name": "SaaS Master",
            "description": "Reach level Master (750 points)",
            "icon": "👑",
            "category": "milestone",
            "points": 250,
            "tier": "legendary",
            "requirement_type": "score",
            "requirement_value": 750
        },
        {
            "name": "Referral King",
            "description": "Refer 10 users",
            "icon": "🎁",
            "category": "referral",
            "points": 300,
            "tier": "legendary",
            "requirement_type": "referrals_count",
            "requirement_value": 10
        },
        {
            "name": "Ultimate Optimizer",
            "description": "Save $1000 total",
            "icon": "🌟",
            "category": "savings",
            "points": 500,
            "tier": "legendary",
            "requirement_type": "total_savings",
            "requirement_value": 1000
        },
    ]
    
    for ach_data in achievements:
        achievement = Achievement(**ach_data)
        db.add(achievement)
    
    db.commit()
    print(f"✅ Seeded {len(achievements)} achievements")
    db.close()

if __name__ == "__main__":
    seed_achievements()
