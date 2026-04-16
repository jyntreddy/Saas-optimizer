"""Add database indexes for performance optimization

Revision ID: 004_add_performance_indexes
Revises: 003_add_gmail_integration
Create Date: 2026-04-16

This migration adds critical indexes to improve query performance:
- Foreign key indexes
- Status and date column indexes
- Composite indexes for common query patterns
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_performance_indexes'
down_revision = '003_add_gmail_integration'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes"""
    
    # =========================================================================
    # Subscriptions table indexes
    # =========================================================================
    # Composite index for user + status queries (common pattern)
    op.create_index(
        'idx_subscriptions_user_status',
        'subscriptions',
        ['user_id', 'status'],
        unique=False
    )
    
    # Index for renewal date queries (for notifications)
    op.create_index(
        'idx_subscriptions_renewal_date',
        'subscriptions',
        ['renewal_date'],
        unique=False
    )
    
    # Index for service name (for grouping and filtering)
    op.create_index(
        'idx_subscriptions_service_name',
        'subscriptions',
        ['service_name'],
        unique=False
    )
    
    # Composite index for active subscriptions by user (very common query)
    op.create_index(
        'idx_subscriptions_user_active',
        'subscriptions',
        ['user_id', 'status', 'renewal_date'],
        unique=False,
        postgresql_where=sa.text("status = 'active'")
    )
    
    # =========================================================================
    # Email Receipts table indexes
    # =========================================================================
    # Index for user_id (foreign key, frequently queried)
    op.create_index(
        'idx_email_receipts_user_id',
        'email_receipts',
        ['user_id'],
        unique=False
    )
    
    # Index for subscription_id (foreign key)
    op.create_index(
        'idx_email_receipts_subscription_id',
        'email_receipts',
        ['subscription_id'],
        unique=False
    )
    
    # Index for sender email (for grouping receipts by vendor)
    op.create_index(
        'idx_email_receipts_sender',
        'email_receipts',
        ['sender_email'],
        unique=False
    )
    
    # Index for received date (for chronological queries)
    op.create_index(
        'idx_email_receipts_received_date',
        'email_receipts',
        ['received_date'],
        unique=False
    )
    
    # Composite index for user + status (for unprocessed receipts)
    op.create_index(
        'idx_email_receipts_user_status',
        'email_receipts',
        ['user_id', 'status'],
        unique=False
    )
    
    # Index for vendor lookup
    op.create_index(
        'idx_email_receipts_vendor',
        'email_receipts',
        ['vendor'],
        unique=False
    )
    
    # =========================================================================
    # Team Members table indexes
    # =========================================================================
    # Index for organization_id (foreign key)
    op.create_index(
        'idx_team_members_org_id',
        'team_members',
        ['organization_id'],
        unique=False
    )
    
    # Index for email (for lookups)
    op.create_index(
        'idx_team_members_email',
        'team_members',
        ['email'],
        unique=False
    )
    
    # Composite index for active members by organization
    op.create_index(
        'idx_team_members_org_active',
        'team_members',
        ['organization_id', 'is_active'],
        unique=False
    )
    
    # =========================================================================
    # Usage Logs table indexes
    # =========================================================================
    # Index for team_member_id (foreign key)
    op.create_index(
        'idx_usage_logs_team_member_id',
        'usage_logs',
        ['team_member_id'],
        unique=False
    )
    
    # Index for subscription_id (foreign key)
    op.create_index(
        'idx_usage_logs_subscription_id',
        'usage_logs',
        ['subscription_id'],
        unique=False
    )
    
    # Index for usage date (for time-based queries)
    op.create_index(
        'idx_usage_logs_usage_date',
        'usage_logs',
        ['usage_date'],
        unique=False
    )
    
    # Composite index for subscription usage over time (analytics queries)
    op.create_index(
        'idx_usage_logs_sub_date',
        'usage_logs',
        ['subscription_id', 'usage_date'],
        unique=False
    )
    
    # Composite index for team member usage analytics
    op.create_index(
        'idx_usage_logs_member_date',
        'usage_logs',
        ['team_member_id', 'usage_date'],
        unique=False
    )
    
    # =========================================================================
    # Subscription Alternatives table indexes (if exists)
    # =========================================================================
    try:
        op.create_index(
            'idx_subscription_alternatives_sub_id',
            'subscription_alternatives',
            ['subscription_id'],
            unique=False
        )
    except Exception:
        pass  # Table might not exist yet
    
    # =========================================================================
    # Negotiation Sessions table indexes (if exists)
    # =========================================================================
    try:
        op.create_index(
            'idx_negotiation_sessions_user_id',
            'negotiation_sessions',
            ['user_id'],
            unique=False
        )
        
        op.create_index(
            'idx_negotiation_sessions_sub_id',
            'negotiation_sessions',
            ['subscription_id'],
            unique=False
        )
        
        op.create_index(
            'idx_negotiation_sessions_status',
            'negotiation_sessions',
            ['status'],
            unique=False
        )
    except Exception:
        pass  # Table might not exist yet
    
    # =========================================================================
    # Gmail Token table indexes (if exists)
    # =========================================================================
    try:
        op.create_index(
            'idx_gmail_tokens_user_id',
            'gmail_tokens',
            ['user_id'],
            unique=False
        )
    except Exception:
        pass  # Table might not exist yet


def downgrade():
    """Remove performance indexes"""
    
    # Subscriptions table
    op.drop_index('idx_subscriptions_user_status', table_name='subscriptions')
    op.drop_index('idx_subscriptions_renewal_date', table_name='subscriptions')
    op.drop_index('idx_subscriptions_service_name', table_name='subscriptions')
    try:
        op.drop_index('idx_subscriptions_user_active', table_name='subscriptions')
    except Exception:
        pass
    
    # Email Receipts table
    op.drop_index('idx_email_receipts_user_id', table_name='email_receipts')
    op.drop_index('idx_email_receipts_subscription_id', table_name='email_receipts')
    op.drop_index('idx_email_receipts_sender', table_name='email_receipts')
    op.drop_index('idx_email_receipts_received_date', table_name='email_receipts')
    op.drop_index('idx_email_receipts_user_status', table_name='email_receipts')
    op.drop_index('idx_email_receipts_vendor', table_name='email_receipts')
    
    # Team Members table
    op.drop_index('idx_team_members_org_id', table_name='team_members')
    op.drop_index('idx_team_members_email', table_name='team_members')
    op.drop_index('idx_team_members_org_active', table_name='team_members')
    
    # Usage Logs table
    op.drop_index('idx_usage_logs_team_member_id', table_name='usage_logs')
    op.drop_index('idx_usage_logs_subscription_id', table_name='usage_logs')
    op.drop_index('idx_usage_logs_usage_date', table_name='usage_logs')
    op.drop_index('idx_usage_logs_sub_date', table_name='usage_logs')
    op.drop_index('idx_usage_logs_member_date', table_name='usage_logs')
    
    # Subscription Alternatives table
    try:
        op.drop_index('idx_subscription_alternatives_sub_id', table_name='subscription_alternatives')
    except Exception:
        pass
    
    # Negotiation Sessions table
    try:
        op.drop_index('idx_negotiation_sessions_user_id', table_name='negotiation_sessions')
        op.drop_index('idx_negotiation_sessions_sub_id', table_name='negotiation_sessions')
        op.drop_index('idx_negotiation_sessions_status', table_name='negotiation_sessions')
    except Exception:
        pass
    
    # Gmail Token table
    try:
        op.drop_index('idx_gmail_tokens_user_id', table_name='gmail_tokens')
    except Exception:
        pass
