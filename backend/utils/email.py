import resend
from itsdangerous import URLSafeTimedSerializer
from ..config import settings

resend.api_key = settings.RESEND_API_KEY

def generate_verification_token(email: str):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt="email-verification")

def verify_token(token: str, expiration: int = 3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt="email-verification", max_age=expiration)
        return email
    except Exception:
        return None

def send_verification_email(email: str, token: str):
    verification_link = f"{settings.BASE_URL}/verify-email.html?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .logo {{ font-size: 24px; font-weight: bold; color: #1a73e8; margin-bottom: 20px; }}
            .title {{ font-size: 20px; font-weight: bold; color: #343a40; margin-bottom: 10px; }}
            .text {{ color: #6c757d; line-height: 1.6; margin-bottom: 20px; }}
            .btn {{ display: inline-block; background-color: #1a73e8; color: #ffffff; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🔗 CampusLink</div>
            <div class="title">Verify Your Email Address</div>
            <p class="text">Thank you for registering on CampusLink — the campus digital marketplace for Crawford University students. Please click the button below to verify your email address and activate your account.</p>
            <a href="{verification_link}" class="btn">Verify My Email</a>
            <p class="text" style="margin-top: 20px;">If you did not create an account on CampusLink, please ignore this email.</p>
            <p class="text">This verification link will expire in <strong>1 hour</strong>.</p>
            <div class="footer">
                &copy; 2024 CampusLink — Crawford University<br>
                This is an automated message, please do not reply.
            </div>
        </div>
    </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from": "CampusLink <onboarding@resend.dev>",
            "to": email,
            "subject": "Verify Your CampusLink Account",
            "html": html_content
        })
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False