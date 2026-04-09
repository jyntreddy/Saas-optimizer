#!/usr/bin/env python3
"""
Database initialization script
Creates initial database tables and optionally seeds with sample data
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import Base, engine
from app.models import User, Subscription
from app.core.config import settings


def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def seed_db():
    """Seed database with sample data"""
    from sqlalchemy.orm import Session
    from app.core.security import get_password_hash
    from datetime import datetime, timedelta
    
    print("Seeding database with sample data...")
    
    with Session(engine) as db:
        # Create sample user
        sample_user = User(
            email="demo@example.com",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True,
            is_superuser=False
        )
        db.add(sample_user)
        db.commit()
        db.refresh(sample_user)
        
        # Create sample subscriptions
        subscriptions = [
            {
                "service_name": "Netflix",
                "provider": "Netflix Inc",
                "cost": 15.99,
                "billing_cycle": "monthly",
                "status": "active",
                "start_date": datetime.now() - timedelta(days=180),
                "renewal_date": datetime.now() + timedelta(days=15),
            },
            {
                "service_name": "Spotify",
                "provider": "Spotify AB",
                "cost": 9.99,
                "billing_cycle": "monthly",
                "status": "active",
                "start_date": datetime.now() - timedelta(days=90),
                "renewal_date": datetime.now() + timedelta(days=20),
            },
            {
                "service_name": "GitHub Pro",
                "provider": "GitHub Inc",
                "cost": 48.00,
                "billing_cycle": "yearly",
                "status": "active",
                "start_date": datetime.now() - timedelta(days=200),
                "renewal_date": datetime.now() + timedelta(days=165),
            },
        ]
        
        for sub_data in subscriptions:
            subscription = Subscription(**sub_data, user_id=sample_user.id)
            db.add(subscription)
        
        db.commit()
        
    print("✓ Database seeded successfully!")
    print("\nSample credentials:")
    print("  Email: demo@example.com")
    print("  Password: demo123")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize database")
    parser.add_argument("--seed", action="store_true", help="Seed with sample data")
    args = parser.parse_args()
    
    init_db()
    
    if args.seed:
        seed_db()
