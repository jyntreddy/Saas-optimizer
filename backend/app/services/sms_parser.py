"""SMS Parsing Service"""

import re
from datetime import datetime
from typing import Optional, Dict, Any
from app.schemas.sms import ParsedSMS


class SMSParser:
    """Service for parsing subscription-related SMS messages"""
    
    # Common patterns for extracting amounts
    AMOUNT_PATTERNS = [
        r'\$\s?(\d+(?:\.\d{2})?)',  # $99.99 or $99
        r'(?:USD|INR|EUR|GBP)\s?(\d+(?:\.\d{2})?)',  # USD 99.99
        r'(?:amount|charged|paid|cost)[:\s]+\$?\s?(\d+(?:\.\d{2})?)',  # amount: $99.99
        r'(\d+(?:\.\d{2})?)\s?(?:USD|INR|EUR|GBP)',  # 99.99 USD
    ]
    
    # Common subscription vendors
    VENDORS = [
        'netflix', 'spotify', 'amazon', 'prime', 'hulu', 'disney',
        'apple', 'google', 'microsoft', 'adobe', 'dropbox', 'zoom',
        'slack', 'github', 'aws', 'azure', 'salesforce', 'notion',
        'figma', 'canva', 'linkedin', 'youtube', 'twitter', 'meta'
    ]
    
    # Keywords that indicate subscription transactions
    SUBSCRIPTION_KEYWORDS = [
        'subscription', 'recurring', 'monthly', 'annual', 'renewal',
        'auto-pay', 'membership', 'premium', 'plan', 'charged'
    ]
    
    @classmethod
    def parse(cls, message: str) -> ParsedSMS:
        """
        Parse SMS message to extract subscription information
        
        Args:
            message: Raw SMS message text
            
        Returns:
            ParsedSMS object with extracted information
        """
        message_lower = message.lower()
        
        # Extract vendor
        vendor = cls._extract_vendor(message_lower)
        
        # Extract amount
        amount = cls._extract_amount(message)
        
        # Extract currency
        currency = cls._extract_currency(message)
        
        # Calculate confidence score
        confidence = cls._calculate_confidence(message_lower, vendor, amount)
        
        return ParsedSMS(
            vendor=vendor,
            amount=amount,
            currency=currency,
            transaction_date=datetime.utcnow(),
            confidence=confidence,
            raw_text=message
        )
    
    @classmethod
    def _extract_vendor(cls, message: str) -> Optional[str]:
        """Extract vendor name from message"""
        for vendor in cls.VENDORS:
            if vendor in message:
                return vendor.capitalize()
        
        # Try to extract from common patterns
        patterns = [
            r'(?:from|by|charged by|billed by)\s+([A-Z][a-zA-Z]+)',
            r'([A-Z][a-zA-Z]+)\s+subscription',
            r'your\s+([A-Z][a-zA-Z]+)\s+(?:account|membership)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()
        
        return None
    
    @classmethod
    def _extract_amount(cls, message: str) -> Optional[float]:
        """Extract amount from message"""
        for pattern in cls.AMOUNT_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    @classmethod
    def _extract_currency(cls, message: str) -> str:
        """Extract currency from message"""
        currencies = ['USD', 'INR', 'EUR', 'GBP', 'CAD', 'AUD']
        message_upper = message.upper()
        
        for currency in currencies:
            if currency in message_upper:
                return currency
        
        # Default to USD if $ sign is present
        if '$' in message:
            return 'USD'
        
        return 'USD'
    
    @classmethod
    def _calculate_confidence(cls, message: str, vendor: Optional[str], amount: Optional[float]) -> float:
        """Calculate confidence score for the parsing"""
        confidence = 0.0
        
        # Base confidence
        if vendor:
            confidence += 0.3
        if amount:
            confidence += 0.3
        
        # Check for subscription keywords
        keyword_count = sum(1 for keyword in cls.SUBSCRIPTION_KEYWORDS if keyword in message)
        confidence += min(keyword_count * 0.1, 0.4)
        
        return min(confidence, 1.0)
    
    @classmethod
    def is_subscription_sms(cls, message: str) -> bool:
        """Check if SMS is likely a subscription transaction"""
        message_lower = message.lower()
        
        # Check for subscription keywords
        has_keywords = any(keyword in message_lower for keyword in cls.SUBSCRIPTION_KEYWORDS)
        
        # Check for amount
        has_amount = any(re.search(pattern, message, re.IGNORECASE) for pattern in cls.AMOUNT_PATTERNS)
        
        # Check for vendor
        has_vendor = any(vendor in message_lower for vendor in cls.VENDORS)
        
        return has_keywords or (has_amount and has_vendor)
