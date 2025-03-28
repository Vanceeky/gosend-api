import jwt
import random
import datetime
import os

from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("secret")
ALGORITHM = os.getenv("algorithm")

OTP_EXPIRY_MINUTES = 5

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def create_otp_token(mobile_number: str, otp: str, role: str):
    """Create a JWT token containing the OTP and role."""
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=OTP_EXPIRY_MINUTES)
    payload = {
        "mobile_number": mobile_number,
        "otp": otp,
        "role": role,  # 🔥 Include the role
        "exp": expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_otp_token(token: str, input_otp: str):
    """Verify the OTP from the token and return mobile_number & role."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["otp"] == input_otp:
            return {"mobile_number": payload["mobile_number"], "role": payload["role"]}  
        return None  # OTP is incorrect
    except jwt.ExpiredSignatureError:
        return "expired"  # OTP has expired
    except jwt.DecodeError:
        return None


def send_otp(mobile_number: str, otp: str):
    """Simulate sending OTP via SMS or email. Replace this with actual SMS API."""
    print(f"📩 Sending OTP {otp} to {mobile_number}")  # Replace with actual API call

def resend_otp(mobile_number: str):
    """Resend a new OTP when the previous one expires."""
    new_otp = generate_otp()
    new_token = create_otp_token(mobile_number, new_otp)
    
    # Send the new OTP
    send_otp(mobile_number, new_otp)
    
    return {"otp_token": new_token, "message": "New OTP has been sent."}
