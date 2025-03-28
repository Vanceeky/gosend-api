import os
import time
import logging
import jwt
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, Depends
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Security settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.getenv("secret")
JWT_ALGORITHM = os.getenv("algorithm")

# Token Expiry Time
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60  # 1 hour


### 🔹 Password Hashing ###
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  


### 🔹 JWT Helper Functions ###
def token_response(token: str):
    return {"access_token": token}

def sign_jwt(user_id: str, account_type: str = None, member_user_id: str = None) -> dict:
    """Generates JWT token with expiration time"""
    expires_at = int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS

    payload = {
        "user_id": user_id,
        "account_type": account_type,
        "member_user_id": member_user_id,
        "expires_at": expires_at  # Store as Unix timestamp
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, JWT_ALGORITHM)
    return token_response(token)

def decode_jwt(token: str) -> dict:
    """Decodes and validates a JWT token"""
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if decoded_token["expires_at"] >= int(time.time()):
            return decoded_token
        else:
            logger.warning("Token expired.")
            return None
    except jwt.PyJWTError:
        logger.warning("Invalid token.")
        return None

def get_jwt_identity(token: str) -> str:

    decoded_token = decode_jwt(token)
    if decoded_token and "user_id" in decoded_token:
        return decoded_token["user_id"]
    return None

### 🔹 JWT Authentication Classes ###

# ✅ Supports Authorization Header (Bearer) Only
class JWTBearerHeader(HTTPBearer):
    """Middleware that validates JWT from Authorization Header"""
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

        return decode_jwt(credentials.credentials)

    def verify_jwt(self, jwtoken: str) -> bool:
        return decode_jwt(jwtoken) is not None


# ✅ Supports Cookies Only
class JWTBearerCookie(HTTPBearer):
    """Middleware that validates JWT from Cookies"""
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if not self.verify_jwt(token):
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

        return decode_jwt(token)

    def verify_jwt(self, jwtoken: str) -> bool:
        return decode_jwt(jwtoken) is not None


# ✅ Supports Both Cookies and Authorization Header
class JWTBearer2(HTTPBearer):
    """Middleware that checks JWT from Cookies or Authorization Header"""
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        token = request.cookies.get("access_token")

        # If not found in cookies, check headers (for Swagger or API clients)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if not self.verify_jwt(token):
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

        return decode_jwt(token)

    def verify_jwt(self, jwtoken: str) -> bool:
        return decode_jwt(jwtoken) is not None



class JWTBearer(HTTPBearer):
    """Middleware that checks JWT from Cookies or Authorization Header"""
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        token = request.cookies.get("access_token")

        # If not found in cookies, check headers (for Swagger or API clients)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        logger.debug(f"Extracted token: {token}")

        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if not self.verify_jwt(token):
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

        return decode_jwt(token)

    def verify_jwt(self, jwtoken: str) -> bool:
        payload = decode_jwt(jwtoken)
        logger.debug(f"Decoded payload: {payload}")
        return payload is not None
    

### 🔹 Role-Based Access Control ###
def require_role2(*allowed_roles: str):
    """Dependency function to enforce role-based access control"""
    def role_dependency(token_payload: dict = Depends(JWTBearer())):
        user_role = token_payload.get("account_type")

        if user_role not in allowed_roles:
            logger.warning(f"Unauthorized access attempt by {user_role}")
            raise HTTPException(status_code=403, detail="Unauthorized access")
        
        return token_payload

    return role_dependency

def require_role(*allowed_roles: str):
    """Dependency function to enforce role-based access control"""
    def role_dependency(token_payload: dict = Depends(JWTBearer())):
        if not token_payload:
            logger.warning("No token payload found")
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user_role = token_payload.get("account_type")
        logger.debug(f"User role: {user_role}, Allowed roles: {allowed_roles}")
        
        if user_role not in allowed_roles:
            logger.warning(f"Unauthorized access attempt by {user_role}")
            raise HTTPException(status_code=403, detail="Unauthorized access")
        
        return token_payload

    return role_dependency

### 🔹 Refresh Token Support (Optional) ###
REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days

def sign_refresh_jwt(user_id: str) -> dict:
    """Generates a refresh JWT token with a longer expiration time"""
    expires_at = int(time.time()) + REFRESH_TOKEN_EXPIRE_SECONDS

    payload = {
        "user_id": user_id,
        "expires_at": expires_at
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, JWT_ALGORITHM)
    return {"refresh_token": token}

def verify_refresh_jwt(token: str) -> bool:
    """Validates refresh token"""
    payload = decode_jwt(token)
    return payload is not None
