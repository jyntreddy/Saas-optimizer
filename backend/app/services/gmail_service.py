"""Gmail API Service"""

import base64
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email import message_from_bytes
from email.header import decode_header
import re

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from ..models.gmail_token import GmailToken
from ..models.email_receipt import EmailReceipt
from ..models.user import User
from .email_parser import EmailParser


class GmailService:
    """Service for interacting with Gmail API"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    @staticmethod
    def get_auth_url(client_id: str, client_secret: str, redirect_uri: str, state: str) -> str:
        """Generate Gmail OAuth authorization URL"""
        from google_auth_oauthlib.flow import Flow
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=GmailService.SCOPES,
            redirect_uri=redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent to get refresh token
        )
        
        return auth_url
    
    @staticmethod
    def exchange_code_for_token(
        code: str, 
        client_id: str, 
        client_secret: str, 
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        from google_auth_oauthlib.flow import Flow
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=GmailService.SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expires_at': credentials.expiry
        }
    
    @staticmethod
    def get_credentials(gmail_token: GmailToken) -> Credentials:
        """Get valid credentials from stored token"""
        creds = Credentials(
            token=gmail_token.access_token,
            refresh_token=gmail_token.refresh_token,
            token_uri=gmail_token.token_uri,
            client_id=gmail_token.client_id,
            client_secret=gmail_token.client_secret,
            scopes=json.loads(gmail_token.scopes) if isinstance(gmail_token.scopes, str) else gmail_token.scopes
        )
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update token in database
            gmail_token.access_token = creds.token
            gmail_token.expires_at = creds.expiry
        
        return creds
    
    @staticmethod
    def scan_emails(
        db: Session,
        user: User,
        max_results: int = 50,
        query: str = "label:receipts OR subject:(receipt OR invoice OR subscription OR payment)"
    ) -> Dict[str, Any]:
        """Scan Gmail for receipt emails"""
        
        # Get Gmail token
        gmail_token = db.query(GmailToken).filter(
            GmailToken.user_id == user.id,
            GmailToken.is_active == True
        ).first()
        
        if not gmail_token:
            return {"error": "Gmail not connected", "receipts_found": 0}
        
        try:
            creds = GmailService.get_credentials(gmail_token)
            service = build('gmail', 'v1', credentials=creds)
            
            # Search for emails
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            receipts_created = 0
            receipts_data = []
            
            for msg in messages:
                # Get full message
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Parse message
                receipt_data = GmailService._parse_gmail_message(message)
                
                # Check if already exists
                existing = db.query(EmailReceipt).filter(
                    EmailReceipt.user_id == user.id,
                    EmailReceipt.gmail_message_id == msg['id']
                ).first()
                
                if existing:
                    continue
                
                # Parse with EmailParser
                parsed = EmailParser.parse_email(
                    receipt_data['subject'],
                    receipt_data['sender'],
                    receipt_data['body']
                )
                
                # Create receipt
                receipt = EmailReceipt(
                    user_id=user.id,
                    gmail_message_id=msg['id'],
                    email_subject=receipt_data['subject'],
                    sender_email=receipt_data['sender'],
                    received_date=receipt_data['date'],
                    raw_body=receipt_data['body'],
                    vendor=parsed.get('vendor'),
                    amount=parsed.get('amount'),
                    currency=parsed.get('currency'),
                    category=parsed.get('category'),
                    confidence_score=parsed.get('confidence_score'),
                    is_subscription=parsed.get('is_subscription', False),
                    extracted_data=parsed.get('extracted_data'),
                    status='pending'
                )
                
                db.add(receipt)
                receipts_created += 1
                receipts_data.append({
                    'subject': receipt_data['subject'],
                    'vendor': parsed.get('vendor'),
                    'amount': parsed.get('amount')
                })
            
            db.commit()
            
            # Update last sync time
            gmail_token.last_synced_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "receipts_found": len(messages),
                "receipts_created": receipts_created,
                "receipts": receipts_data
            }
            
        except HttpError as error:
            return {
                "error": f"Gmail API error: {error}",
                "receipts_found": 0
            }
    
    @staticmethod
    def _parse_gmail_message(message: Dict) -> Dict[str, Any]:
        """Parse Gmail message to extract subject, sender, body, date"""
        headers = message['payload']['headers']
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        # Parse date
        from email.utils import parsedate_to_datetime
        try:
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.utcnow()
        
        # Extract email from sender (remove display name)
        email_match = re.search(r'<(.+?)>', sender)
        if email_match:
            sender = email_match.group(1)
        
        # Get body
        body = GmailService._get_message_body(message['payload'])
        
        return {
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body
        }
    
    @staticmethod
    def _get_message_body(payload: Dict) -> str:
        """Extract body from message payload"""
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        # Strip HTML tags
                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        return re.sub('<[^<]+?>', '', html)
                elif 'parts' in part:
                    # Recursive for multipart
                    body = GmailService._get_message_body(part)
                    if body:
                        return body
        
        return ''
    
    @staticmethod
    def disconnect(db: Session, user: User) -> bool:
        """Disconnect Gmail integration"""
        gmail_token = db.query(GmailToken).filter(
            GmailToken.user_id == user.id
        ).first()
        
        if gmail_token:
            gmail_token.is_active = False
            db.commit()
            return True
        
        return False
