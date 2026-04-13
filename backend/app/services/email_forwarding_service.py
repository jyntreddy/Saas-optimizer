"""Email Forwarding Service"""

import email
from email import policy
from email.parser import BytesParser
from typing import Dict, Any, Optional
import re
from datetime import datetime


class EmailForwardingService:
    """Parse forwarded email messages in MIME format"""
    
    @staticmethod
    def parse_forwarded_email(raw_email: str) -> Dict[str, Any]:
        """
        Parse raw email (MIME format) forwarded to receipts@domain.com
        
        Handles various email formats:
        - Plain MIME emails
        - Forwarded emails
        - Multipart emails with attachments
        
        Returns:
            Dict with subject, sender, body, date, headers
        """
        try:
            # Parse email
            if isinstance(raw_email, str):
                msg = email.message_from_string(raw_email, policy=policy.default)
            else:
                msg = email.message_from_bytes(raw_email, policy=policy.default)
            
            # Extract headers
            subject = EmailForwardingService._decode_header(msg.get('Subject', ''))
            from_addr = msg.get('From', '')
            to_addr = msg.get('To', '')
            date_str = msg.get('Date', '')
            
            # Extract sender email
            sender_email = EmailForwardingService._extract_email(from_addr)
            
            # Parse date
            from email.utils import parsedate_to_datetime
            try:
                received_date = parsedate_to_datetime(date_str)
            except:
                received_date = datetime.utcnow()
            
            # Extract body
            body = EmailForwardingService._extract_body(msg)
            
            # Extract any metadata
            message_id = msg.get('Message-ID', '')
            
            return {
                'subject': subject,
                'sender': sender_email,
                'from_header': from_addr,
                'to': to_addr,
                'date': received_date,
                'body': body,
                'message_id': message_id,
                'headers': dict(msg.items())
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse email: {str(e)}")
    
    @staticmethod
    def _decode_header(header: str) -> str:
        """Decode email header (handles encoding)"""
        if not header:
            return ""
        
        decoded_parts = email.header.decode_header(header)
        decoded_str = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += part
        
        return decoded_str.strip()
    
    @staticmethod
    def _extract_email(from_header: str) -> str:
        """Extract email address from 'From' header"""
        # Match email in angle brackets: "Name <email@domain.com>"
        match = re.search(r'<(.+?)>', from_header)
        if match:
            return match.group(1).strip()
        
        # Match standalone email
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_header)
        if match:
            return match.group(0).strip()
        
        return from_header.strip()
    
    @staticmethod
    def _extract_body(msg) -> str:
        """Extract email body (prefers plain text, falls back to HTML)"""
        body = ""
        
        if msg.is_multipart():
            # Multipart email (usually HTML + plain text)
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get plain text
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
                
                # Fallback to HTML
                elif content_type == "text/html" and not body:
                    try:
                        html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Strip HTML tags
                        body = re.sub('<[^<]+?>', '', html)
                    except:
                        pass
        else:
            # Single part email
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return body.strip()
    
    @staticmethod
    def identify_user_by_email(email_address: str) -> Optional[str]:
        """
        Identify which user forwarded the email
        
        This can be done by:
        1. Email domain matching
        2. User registration of forwarding email
        3. Unique forwarding address per user (receipts+user123@domain.com)
        
        Returns user identifier (email or ID)
        """
        # Check for plus addressing: receipts+user123@domain.com
        match = re.search(r'\+(.+?)@', email_address)
        if match:
            return match.group(1)
        
        # Otherwise, return the full email
        return email_address
