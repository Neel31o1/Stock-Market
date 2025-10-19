"""
Email Service - Clean email sending functionality
Handles SMTP connection and template rendering
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Handle all email operations"""
    
    def __init__(self, smtp_server, smtp_port, email_from, email_password):
        """
        Initialize email service
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            email_from: Sender email
            email_password: Email password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_from = email_from
        self.email_password = email_password
    
    def load_template(self, template_path):
        """
        Load HTML email template
        
        Args:
            template_path: Path to HTML template
        
        Returns:
            str: Template content
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error loading template: {e}")
            return None
    
    def render_template(self, template, data):
        """
        Render template with data
        
        Args:
            template: HTML template string
            data: Dictionary with template variables
        
        Returns:
            str: Rendered HTML
        """
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))
        return template
    
    def send_email(self, recipients, subject, html_content, text_content=None):
        """
        Send email to recipients
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text alternative (optional)
        
        Returns:
            bool: True if sent successfully
        """
        try:
            # Ensure recipients is a list
            if isinstance(recipients, str):
                recipients = [recipients]
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Attach plain text if provided
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Attach HTML
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to: {', '.join(recipients)}")
            return True
        
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
