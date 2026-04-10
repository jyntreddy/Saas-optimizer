"""Email parser service for extracting subscription receipts"""

import re
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.email_receipt import EmailReceipt


class EmailParser:
    """Parse email receipts to extract subscription information"""
    
    VENDOR_PATTERNS = {
        'netflix': r'netflix',
        'spotify': r'spotify',
        'amazon': r'amazon\s*(prime|web\s*services|aws)',
        'microsoft': r'microsoft|office\s*365|azure',
        'google': r'google\s*(workspace|cloud|one)',
        'adobe': r'adobe\s*(creative\s*cloud)?',
        'dropbox': r'dropbox',
        'zoom': r'zoom',
        'slack': r'slack',
        'github': r'github',
        'atlassian': r'atlassian|jira|confluence',
        'salesforce': r'salesforce',
        'hubspot': r'hubspot',
        'intercom': r'intercom',
        'mailchimp': r'mailchimp',
        'sendgrid': r'sendgrid',
        'twilio': r'twilio',
        'stripe': r'stripe',
        'heroku': r'heroku',
        'digitalocean': r'digitalocean',
    }
    
    AMOUNT_PATTERNS = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(?:USD|usd)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(?:total|amount|charged)[:=\s]+\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|usd)',
    ]
    
    SUBSCRIPTION_KEYWORDS = [
        'subscription', 'renewal', 'recurring', 'monthly', 'yearly',
        'billing', 'invoice', 'payment', 'charged', 'receipt'
    ]
    
    @classmethod
    def parse_email(cls, subject: str, sender: str, body: str) -> Dict[str, Any]:
        """Parse email to extract subscription data"""
        
        combined_text = f"{subject} {body}".lower()
        
        # Extract vendor
        vendor = cls._extract_vendor(combined_text)
        
        # Extract amount
        amount, currency = cls._extract_amount(combined_text)
        
        # Check if subscription-related
        is_subscription = cls._detect_subscription(combined_text)
        
        # Calculate confidence
        confidence = cls._calculate_confidence(vendor, amount, is_subscription)
        
        # Extract category
        category = cls._categorize_vendor(vendor) if vendor else None
        
        return {
            'vendor': vendor,
            'amount': amount,
            'currency': currency,
            'is_subscription': is_subscription,
            'confidence_score': confidence,
            'category': category,
            'extracted_data': {
                'subject': subject,
                'sender': sender,
                'detected_keywords': cls._get_matching_keywords(combined_text)
            }
        }
    
    @classmethod
    def _extract_vendor(cls, text: str) -> Optional[str]:
        """Extract vendor name from text"""
        for vendor, pattern in cls.VENDOR_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return vendor
        return None
    
    @classmethod
    def _extract_amount(cls, text: str) -> tuple:
        """Extract amount and currency"""
        for pattern in cls.AMOUNT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str), 'USD'
                except ValueError:
                    continue
        return None, None
    
    @classmethod
    def _detect_subscription(cls, text: str) -> bool:
        """Check if email is subscription-related"""
        keyword_count = sum(1 for keyword in cls.SUBSCRIPTION_KEYWORDS if keyword in text)
        return keyword_count >= 2
    
    @classmethod
    def _calculate_confidence(cls, vendor: Optional[str], amount: Optional[float], 
                             is_subscription: bool) -> float:
        """Calculate confidence score 0-1.0"""
        score = 0.0
        if vendor:
            score += 0.4
        if amount:
            score += 0.3
        if is_subscription:
            score += 0.3
        return round(score, 2)
    
    @classmethod
    def _categorize_vendor(cls, vendor: Optional[str]) -> Optional[str]:
        """Categorize vendor by type"""
        categories = {
            'productivity': ['microsoft', 'google', 'adobe', 'atlassian', 'notion'],
            'cloud': ['amazon', 'azure', 'google', 'heroku', 'digitalocean'],
            'communication': ['zoom', 'slack', 'intercom', 'twilio'],
            'development': ['github', 'gitlab', 'docker'],
            'marketing': ['hubspot', 'mailchimp', 'sendgrid'],
            'entertainment': ['netflix', 'spotify', 'youtube'],
            'storage': ['dropbox', 'google', 'box'],
        }
        
        for category, vendors in categories.items():
            if vendor and vendor in vendors:
                return category
        return 'other'
    
    @classmethod
    def _get_matching_keywords(cls, text: str) -> list:
        """Get all matching subscription keywords"""
        return [kw for kw in cls.SUBSCRIPTION_KEYWORDS if kw in text]
