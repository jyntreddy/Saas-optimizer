import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings


class EmailService:
    """Email notification service"""
    
    @staticmethod
    def send_email(to: str, subject: str, body: str):
        """Send email notification"""
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            print("Email settings not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USER
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_renewal_reminder(user_email: str, subscription_name: str, renewal_date: str):
        """Send subscription renewal reminder"""
        subject = f"Reminder: {subscription_name} renewing soon"
        body = f"""
        <html>
            <body>
                <h2>Subscription Renewal Reminder</h2>
                <p>Your subscription to <strong>{subscription_name}</strong> will renew on {renewal_date}.</p>
                <p>Review your subscription in the SaaS Optimizer dashboard.</p>
            </body>
        </html>
        """
        return EmailService.send_email(user_email, subject, body)
