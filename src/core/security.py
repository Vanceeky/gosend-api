from passlib.context import CryptContext

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException

import jwt
import os
import time



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.getenv("secret")
JWT_ALGORITHM = os.getenv("algorithm")



def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_id: str, account_type: str = None) -> dict:
    # Set expiration time (1 hour from now)
    expires_at = int(time.time()) + (60 * 60)

    payload = {
        "user_id": user_id,
        "account_type": account_type,
        "expires_at": expires_at  # Store as Unix timestamp
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, JWT_ALGORITHM)

    return token_response(token)

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Validate if the token has expired
        if decoded_token["expires_at"] >= int(time.time()):
            return decoded_token
        else:
            return None  # Expired token

    except jwt.PyJWTError:
        return {}



class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

        return credentials.credentials

    def verify_jwt(self, jwtoken: str) -> bool:
        """Verify if the JWT token is valid and not expired."""
        payload = decode_jwt(jwtoken)
        return payload is not None  # Returns True if valid, False if expired/invalid


