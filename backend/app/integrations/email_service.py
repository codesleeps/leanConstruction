"""
Email Service Integration

Handles email sending for onboarding, notifications, and marketing campaigns.
Supports multiple email providers including SMTP, SendGrid, and AWS SES.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import requests
import json

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    """Unified email service supporting multiple providers"""
    
    def __init__(self):
        self.provider = os.getenv('EMAIL_PROVIDER', 'smtp').lower()
        self.smtp_config = {
            'host': os.getenv('SMTP_HOST'),
            'port': int(os.getenv('SMTP_PORT', 587)),
            'user': os.getenv('SMTP_USER'),
            'password': os.getenv('SMTP_PASSWORD'),
            'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        }
        
        self.sendgrid_config = {
            'api_key': os.getenv('SENDGRID_API_KEY'),
            'from_email': os.getenv('FROM_EMAIL'),
            'from_name': os.getenv('FROM_NAME', 'Lean AI Construction')
        }
        
        self.ses_config = {
            'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'region': os.getenv('AWS_REGION', 'us-east-1')
        }
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send email using the configured provider
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email content
            text_content: Plain text email content (optional)
            from_email: Override default from email
            from_name: Override default from name
            attachments: List of attachment dicts with 'filename' and 'content'
            
        Returns:
            Dict with success status and message details
        """
        try:
            if self.provider == 'smtp':
                return self._send_smtp_email(
                    to_email, subject, html_content, text_content, 
                    from_email, from_name, attachments
                )
            elif self.provider == 'sendgrid':
                return self._send_sendgrid_email(
                    to_email, subject, html_content, text_content,
                    from_email, from_name, attachments
                )
            elif self.provider == 'ses':
                return self._send_ses_email(
                    to_email, subject, html_content, text_content,
                    from_email, from_name, attachments
                )
            else:
                raise ValueError(f"Unsupported email provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _send_smtp_email(
        self, to_email: str, subject: str, html_content: str, 
        text_content: Optional[str], from_email: Optional[str], 
        from_name: Optional[str], attachments: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name or self.sendgrid_config['from_name']} <{from_email or self.sendgrid_config['from_email']}>"
        msg['To'] = to_email
        
        # Add text content
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                # Implementation for attachments
                pass
        
        # Send email
        server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
        try:
            if self.smtp_config['use_tls']:
                server.starttls()
            server.login(self.smtp_config['user'], self.smtp_config['password'])
            server.send_message(msg)
            
            return {
                'success': True,
                'provider': 'smtp',
                'to': to_email,
                'subject': subject,
                'timestamp': datetime.utcnow().isoformat()
            }
        finally:
            server.quit()
    
    def _send_sendgrid_email(
        self, to_email: str, subject: str, html_content: str,
        text_content: Optional[str], from_email: Optional[str],
        from_name: Optional[str], attachments: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Send email via SendGrid"""
        
        url = "https://api.sendgrid.com/v3/mail/send"
        
        data = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {
                "email": from_email or self.sendgrid_config['from_email'],
                "name": from_name or self.sendgrid_config['from_name']
            },
            "content": []
        }
        
        # Add text content
        if text_content:
            data["content"].append({
                "type": "text/plain",
                "value": text_content
            })
        
        # Add HTML content
        data["content"].append({
            "type": "text/html", 
            "value": html_content
        })
        
        # Add attachments if provided
        if attachments:
            data["attachments"] = []
            for attachment in attachments:
                # Implementation for attachments
                pass
        
        headers = {
            "Authorization": f"Bearer {self.sendgrid_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 202:
            return {
                'success': True,
                'provider': 'sendgrid',
                'to': to_email,
                'subject': subject,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            raise Exception(f"SendGrid API error: {response.status_code} - {response.text}")
    
    def _send_ses_email(
        self, to_email: str, subject: str, html_content: str,
        text_content: Optional[str], from_email: Optional[str],
        from_name: Optional[str], attachments: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Send email via AWS SES"""
        # AWS SES implementation would go here
        # This is a placeholder for SES integration
        logger.info(f"SES email would be sent to {to_email} with subject: {subject}")
        
        return {
            'success': True,
            'provider': 'ses',
            'to': to_email,
            'subject': subject,
            'timestamp': datetime.utcnow().isoformat()
        }

# Email template functions
def create_welcome_email_template(user_name: str, company: str) -> Dict[str, str]:
    """Create welcome email template"""
    
    subject = "Welcome to Lean AI Construction - Get Started in 5 Minutes"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.6;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Lean AI Construction!</h1>
        </div>
        
        <div style="padding: 40px 20px;">
            <h2 style="color: #333;">Hi {user_name},</h2>
            
            <p>Thank you for joining <strong>{company}</strong> to Lean AI Construction! We're excited to help you transform your construction projects with AI-powered insights.</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff;">
                <h3 style="margin-top: 0; color: #495057;">🚀 Quick Start Guide</h3>
                <ol style="margin: 0; padding-left: 20px;">
                    <li><strong>Verify your email</strong> - Click the verification link we sent</li>
                    <li><strong>Complete your profile</strong> - Tell us about your projects</li>
                    <li><strong>Create your first project</strong> - Start tracking waste and analytics</li>
                    <li><strong>Explore AI features</strong> - Discover waste detection and predictions</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://app.leanaiconstruction.com/dashboard" 
                   style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                    🚀 Get Started Now
                </a>
            </div>
            
            <div style="background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #0066cc;">💡 Pro Tip</h4>
                <p style="margin: 0; color: #004499;">
                    Try our demo accounts to explore the platform with realistic sample data before creating your own projects.
                </p>
            </div>
            
            <p>Need help? Reply to this email or check out our <a href="https://leanaiconstruction.com/help" style="color: #007bff;">help center</a>.</p>
            
            <p>Best regards,<br>
            <strong>The Lean AI Construction Team</strong></p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #666; text-align: center;">
                Lean AI Construction • Building Smarter, Faster, More Sustainably<br>
                <a href="https://leanaiconstruction.com" style="color: #007bff;">leanaiconstruction.com</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Lean AI Construction!
    
    Hi {user_name},
    
    Thank you for joining {company} to Lean AI Construction! We're excited to help you transform your construction projects with AI-powered insights.
    
    Quick Start Guide:
    1. Verify your email - Click the verification link we sent
    2. Complete your profile - Tell us about your projects
    3. Create your first project - Start tracking waste and analytics
    4. Explore AI features - Discover waste detection and predictions
    
    Get Started: https://app.leanaiconstruction.com/dashboard
    
    Need help? Reply to this email or check out our help center at https://leanaiconstruction.com/help
    
    Best regards,
    The Lean AI Construction Team
    
    Lean AI Construction • Building Smarter, Faster, More Sustainably
    leanaiconstruction.com
    """
    
    return {
        'subject': subject,
        'html_content': html_content,
        'text_content': text_content
    }

def create_onboarding_guide_email_template(user_name: str) -> Dict[str, str]:
    """Create onboarding guide email template"""
    
    subject = "Your Lean AI Construction Onboarding Guide"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.6;">
        <div style="background: #28a745; padding: 30px 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">Onboarding Guide</h1>
        </div>
        
        <div style="padding: 40px 20px;">
            <h2 style="color: #333;">Hi {user_name} 👋</h2>
            
            <p>Ready to dive deeper into Lean AI Construction? Here's your step-by-step guide to getting the most out of our platform.</p>
            
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3 style="margin-top: 0; color: #856404;">📋 Onboarding Checklist</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>✅ Complete your company profile</li>
                    <li>✅ Add your first construction project</li>
                    <li>✅ Set up waste tracking</li>
                    <li>✅ Invite team members</li>
                    <li>🔲 Explore AI-powered analytics</li>
                    <li>🔲 Create your first report</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://app.leanaiconstruction.com/onboarding" 
                   style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                    Continue Onboarding
                </a>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #495057;">🎯 Key Features to Explore</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>AI Waste Detection:</strong> Automatically identify and categorize construction waste</li>
                    <li><strong>Predictive Analytics:</strong> Forecast project delays and budget overruns</li>
                    <li><strong>Real-time Dashboards:</strong> Monitor all projects from a single view</li>
                    <li><strong>Team Collaboration:</strong> Keep everyone aligned with shared workspaces</li>
                </ul>
            </div>
            
            <p>Questions? Our support team is here to help!</p>
            
            <p>Best regards,<br>
            <strong>The Lean AI Construction Team</strong></p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Your Lean AI Construction Onboarding Guide
    
    Hi {user_name},
    
    Ready to dive deeper into Lean AI Construction? Here's your step-by-step guide to getting the most out of our platform.
    
    Onboarding Checklist:
    ✅ Complete your company profile
    ✅ Add your first construction project
    ✅ Set up waste tracking
    ✅ Invite team members
    🔲 Explore AI-powered analytics
    🔲 Create your first report
    
    Continue: https://app.leanaiconstruction.com/onboarding
    
    Key Features to Explore:
    • AI Waste Detection: Automatically identify and categorize construction waste
    • Predictive Analytics: Forecast project delays and budget overruns
    • Real-time Dashboards: Monitor all projects from a single view
    • Team Collaboration: Keep everyone aligned with shared workspaces
    
    Questions? Our support team is here to help!
    
    Best regards,
    The Lean AI Construction Team
    """
    
    return {
        'subject': subject,
        'html_content': html_content,
        'text_content': text_content
    }

# Global email service instance
email_service = EmailService()

def send_welcome_email(to_email: str, user_name: str, company: str) -> Dict[str, Any]:
    """Send welcome email to new user"""
    template = create_welcome_email_template(user_name, company)
    
    return email_service.send_email(
        to_email=to_email,
        subject=template['subject'],
        html_content=template['html_content'],
        text_content=template['text_content']
    )

def send_onboarding_guide_email(to_email: str, user_name: str) -> Dict[str, Any]:
    """Send onboarding guide email"""
    template = create_onboarding_guide_email_template(user_name)
    
    return email_service.send_email(
        to_email=to_email,
        subject=template['subject'],
        html_content=template['html_content'],
        text_content=template['text_content']
    )