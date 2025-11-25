"""
Email Service
Handles sending transactional emails (welcome, password reset, notifications)
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

from backend.config import settings


class EmailService:
    """Service for sending emails via SMTP"""
    
    @staticmethod
    async def send_welcome_email(email: str, name: str) -> bool:
        """
        Send welcome email to new user
        
        Args:
            email: User's email address
            name: User's full name
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f9fafb;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .logo {{
            font-size: 36px;
            font-weight: bold;
            background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 24px;
        }}
        h1 {{ 
            color: #111827; 
            font-size: 24px; 
            margin: 24px 0 16px; 
        }}
        p {{ 
            color: #6b7280; 
            font-size: 16px; 
            line-height: 1.6; 
            margin-bottom: 16px; 
        }}
        ul {{ 
            color: #6b7280; 
            line-height: 1.8; 
            margin: 16px 0;
            padding-left: 24px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
            color: white !important;
            text-decoration: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-weight: 600;
            margin: 24px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #e5e7eb;
            color: #9ca3af;
            font-size: 14px;
        }}
        .footer p {{
            color: #9ca3af;
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Gamma</div>
        <h1>Welcome to Gamma, {name}! 🎉</h1>
        <p>Thank you for creating your account. We're excited to have you on board!</p>
        <p>Gamma is a new medium for presenting ideas, powered by AI. You can now:</p>
        <ul>
            <li>Create beautiful presentations in seconds</li>
            <li>Use AI to generate content and images</li>
            <li>Choose from dozens of themes and templates</li>
            <li>Collaborate with your team in real-time</li>
            <li>Present from any device</li>
        </ul>
        <a href="http://localhost:3000/home" class="button">Get Started</a>
        <p>If you have any questions, our support team is here to help!</p>
        <div class="footer">
            <p>© 2024 Gamma. All rights reserved.</p>
            <p>You're receiving this email because you signed up for Gamma.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Create plain text version as fallback
        text = f"""
Welcome to Gamma, {name}!

Thank you for creating your account. We're excited to have you on board!

Gamma is a new medium for presenting ideas, powered by AI. You can now:

• Create beautiful presentations in seconds
• Use AI to generate content and images
• Choose from dozens of themes and templates
• Collaborate with your team in real-time
• Present from any device

Get started at: http://localhost:3000/home

If you have any questions, our support team is here to help!

© 2024 Gamma. All rights reserved.
You're receiving this email because you signed up for Gamma.
        """
        
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Welcome to Gamma! 🎉'
        message['From'] = f"{getattr(settings, 'SMTP_FROM_NAME', 'Gamma')} <{getattr(settings, 'SMTP_FROM', 'noreply@gamma.com')}>"
        message['To'] = email
        
        # Attach both plain text and HTML versions
        text_part = MIMEText(text, 'plain')
        html_part = MIMEText(html, 'html')
        message.attach(text_part)
        message.attach(html_part)
        
        try:
            # Get SMTP settings from environment
            smtp_host = getattr(settings, 'SMTP_HOST', None)
            smtp_port = getattr(settings, 'SMTP_PORT', 587)
            smtp_user = getattr(settings, 'SMTP_USER', None)
            smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
            
            # Skip if SMTP not configured (development mode)
            if not smtp_host or not smtp_user or not smtp_password:
                print(f"⚠️  SMTP not configured. Email would be sent to {email}")
                print(f"📧 Subject: {message['Subject']}")
                return True
            
            # Send email via SMTP
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=int(smtp_port),
                username=smtp_user,
                password=smtp_password,
                start_tls=True
            )
            
            print(f"✅ Welcome email sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {str(e)}")
            # Don't fail registration if email fails
            return False
    
    
    @staticmethod
    async def send_password_reset_email(email: str, name: str, reset_token: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: User's email address
            name: User's full name
            reset_token: Password reset token
            
        Returns:
            bool: True if sent successfully
        """
        
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f9fafb;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .logo {{
            font-size: 36px;
            font-weight: bold;
            background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 24px;
        }}
        h1 {{ color: #111827; font-size: 24px; margin: 24px 0 16px; }}
        p {{ color: #6b7280; font-size: 16px; line-height: 1.6; margin-bottom: 16px; }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
            color: white !important;
            text-decoration: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-weight: 600;
            margin: 24px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #e5e7eb;
            color: #9ca3af;
            font-size: 14px;
        }}
        .warning {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px 16px;
            margin: 16px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Gamma</div>
        <h1>Reset your password</h1>
        <p>Hi {name},</p>
        <p>We received a request to reset your password. Click the button below to create a new password:</p>
        <a href="{reset_url}" class="button">Reset Password</a>
        <p>This link will expire in 1 hour for security reasons.</p>
        <div class="warning">
            <p style="color: #92400e; margin: 0;">
                <strong>Didn't request this?</strong> You can safely ignore this email. Your password won't change.
            </p>
        </div>
        <div class="footer">
            <p>© 2024 Gamma. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Reset your Gamma password'
        message['From'] = f"{getattr(settings, 'SMTP_FROM_NAME', 'Gamma')} <{getattr(settings, 'SMTP_FROM', 'noreply@gamma.com')}>"
        message['To'] = email
        
        html_part = MIMEText(html, 'html')
        message.attach(html_part)
        
        try:
            smtp_host = getattr(settings, 'SMTP_HOST', None)
            smtp_port = getattr(settings, 'SMTP_PORT', 587)
            smtp_user = getattr(settings, 'SMTP_USER', None)
            smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
            
            if not smtp_host or not smtp_user or not smtp_password:
                print(f"⚠️  SMTP not configured. Password reset email would be sent to {email}")
                print(f"🔗 Reset URL: {reset_url}")
                return True
            
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=int(smtp_port),
                username=smtp_user,
                password=smtp_password,
                start_tls=True
            )
            
            print(f"✅ Password reset email sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send password reset email to {email}: {str(e)}")
            return False
