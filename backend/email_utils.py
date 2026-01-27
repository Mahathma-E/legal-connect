"""
Email utility functions for LegalConnect
Handles email verification and password reset emails via SMTP
"""

from flask_mail import Mail, Message
import secrets
from datetime import datetime, timedelta
import os

def generate_verification_token():
    """Generate a cryptographically secure verification token"""
    return secrets.token_urlsafe(32)

def generate_token_expiry(hours=24):
    """Generate token expiry time (default 24 hours from now)"""
    return (datetime.now() + timedelta(hours=hours)).isoformat()

def is_token_expired(expiry_time_str):
    """Check if a token has expired"""
    if not expiry_time_str:
        return True
    try:
        expiry_time = datetime.fromisoformat(expiry_time_str)
        return datetime.now() > expiry_time
    except (ValueError, TypeError):
        return True

def send_verification_email(mail, user_email, user_name, token):
    """
    Send email verification link to user
    
    Args:
        mail: Flask-Mail instance
        user_email: User's email address
        user_name: User's name
        token: Verification token
    """
    try:
        # Get frontend URL from environment or use default
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3001')
        verification_link = f"{frontend_url}/verify-email/{token}"
        
        msg = Message(
            subject="Verify Your LegalConnect Account",
            recipients=[user_email],
            sender=os.getenv('MAIL_DEFAULT_SENDER')
        )
        
        # HTML email body
        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #667eea;">Welcome to LegalConnect!</h2>
                    
                    <p>Hello <strong>{user_name}</strong>,</p>
                    
                    <p>Thank you for registering with LegalConnect. Please verify your email address to activate your account.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_link}" 
                           style="background-color: #667eea; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {verification_link}
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        <strong>Note:</strong> This link will expire in 24 hours.
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        If you didn't create this account, please ignore this email.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        Best regards,<br>
                        LegalConnect Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text fallback
        msg.body = f"""
Hello {user_name},

Thank you for registering with LegalConnect!

Please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
LegalConnect Team
        """
        
        print(f"[EMAIL] Attempting to send verification email to {user_email}")
        mail.send(msg)
        print(f"[EMAIL] ✅ Successfully sent verification email to {user_email}")
        return True
    except Exception as e:
        # Detailed error logging for debugging
        error_type = type(e).__name__
        error_message = str(e)
        
        print(f"[EMAIL ERROR] ❌ Failed to send verification email to {user_email}")
        print(f"[EMAIL ERROR] Error Type: {error_type}")
        print(f"[EMAIL ERROR] Error Message: {error_message}")
        
        # Check for common Gmail SMTP errors
        if "Authentication" in error_message or "Username and Password not accepted" in error_message:
            print("[EMAIL ERROR] 🔐 SMTP Authentication Failed!")
            print("[EMAIL ERROR] Possible causes:")
            print("[EMAIL ERROR]   1. Gmail App Password is incorrect or missing")
            print("[EMAIL ERROR]   2. 2-Step Verification not enabled on Gmail account")
            print("[EMAIL ERROR]   3. Wrong Gmail username in .env file")
            print("[EMAIL ERROR] Solution: Generate a new App Password at https://myaccount.google.com/apppasswords")
        elif "Connection" in error_message or "timed out" in error_message:
            print("[EMAIL ERROR] 🌐 SMTP Connection Failed!")
            print("[EMAIL ERROR] Possible causes:")
            print("[EMAIL ERROR]   1. No internet connection")
            print("[EMAIL ERROR]   2. Firewall blocking port 587")
            print("[EMAIL ERROR]   3. Gmail SMTP server unreachable")
        elif "MAIL_USERNAME" in error_message or "MAIL_PASSWORD" in error_message:
            print("[EMAIL ERROR] ⚙️ SMTP Configuration Missing!")
            print("[EMAIL ERROR] Please configure MAIL_USERNAME and MAIL_PASSWORD in backend/.env file")
        
        import traceback
        traceback.print_exc()

        # FALLBACK FOR DEMO: Print link to console if email fails
        print("\n" + "="*60)
        print("📢 [DEMO MODE] EMAIL DELIVERY FAILED (Expected without SMTP setup)")
        print(f"🔗 Verification Link: {verification_link}")
        print("="*60 + "\n")
        
        return False

def send_password_reset_email(mail, user_email, user_name, token):
    """
    Send password reset link to user
    
    Args:
        mail: Flask-Mail instance
        user_email: User's email address
        user_name: User's name
        token: Reset token
    """
    try:
        # Get frontend URL from environment or use default
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3001')
        reset_link = f"{frontend_url}/reset-password/{token}"
        
        msg = Message(
            subject="Reset Your LegalConnect Password",
            recipients=[user_email],
            sender=os.getenv('MAIL_DEFAULT_SENDER')
        )
        
        # HTML email body
        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #667eea;">Password Reset Request</h2>
                    
                    <p>Hello <strong>{user_name}</strong>,</p>
                    
                    <p>We received a request to reset your password for your LegalConnect account.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="background-color: #667eea; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {reset_link}
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        <strong>Note:</strong> This link will expire in 24 hours.
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        Best regards,<br>
                        LegalConnect Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text fallback
        msg.body = f"""
Hello {user_name},

We received a request to reset your password.

Click the link below to reset your password:

{reset_link}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
LegalConnect Team
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        
        # FALLBACK FOR DEMO: Print link to console if email fails
        print("\n" + "="*60)
        print("📢 [DEMO MODE] EMAIL DELIVERY FAILED (Expected without SMTP setup)")
        print(f"🔗 Password Reset Link: {reset_link}")
        print("="*60 + "\n")

        # Also write to file for guaranteed access
        try:
            with open('reset_link.txt', 'w') as f:
                f.write(f"Password Reset Link: {reset_link}\n")
            print(f"✅ Reset link written to reset_link.txt")
        except Exception as file_error:
            print(f"Failed to write reset link to file: {file_error}")

        return False

def send_resend_verification_email(mail, user_email, user_name, token):
    """
    Resend verification email (same as send_verification_email but with different subject)
    """
    return send_verification_email(mail, user_email, user_name, token)
