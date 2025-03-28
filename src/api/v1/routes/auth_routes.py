from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.services.auth_services import AuthService  # Import service layer
from core.database import get_db  # Import DB session
from api.v1.repo.member_repo import MemberRepo

from core.security import hash_password
from fastapi import Response

router = APIRouter()

@router.post("/login")
async def login(mobile_number: str, role: str, db: AsyncSession = Depends(get_db)):
    """
    API endpoint to initiate login by sending OTP.
    """
    return await AuthService.login(db, mobile_number, role)

@router.post("/verify-otp")
async def verify_otp(mobile_number: str, input_otp: str):
    """
    API endpoint to verify OTP.
    """
    return await AuthService.verify_otp(mobile_number, input_otp)

@router.post("/verify-mpin")
async def verify_mpin(
    mobile_number: str, 
    input_mpin: str, 
    role: str,  
    response: Response,  
    db: AsyncSession = Depends(get_db),
):
    """
    API endpoint to verify MPIN and issue JWT token.
    """
    result = await AuthService.verify_mpin(db, mobile_number, input_mpin, role)

    # Save the access token in cookies
    response.set_cookie(
        key="access_token", 
        value=result["access_token"]["access_token"],  
        httponly=False,  
        secure=False,  
        samesite="Lax",  
        max_age=86400,  
        path="/",  
    )

    # Save the account type in cookies
    response.set_cookie(
        key="account_type",
        value=role,  
        httponly=False,  # Optional: Set to False if frontend needs access
        secure=False,  
        samesite="Lax",  
        max_age=86400,  
        path="/",  
    )

    # Save the account type in cookies
    response.set_cookie(
        key="member_user_id",
        value=result["member_user_id"],  
        httponly=False,  # Optional: Set to False if frontend needs access
        secure=False,  
        samesite="Lax",  
        max_age=86400,  
        path="/",  
    )

    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return {
        "access_token": result["access_token"]["access_token"],
        "account_type": role
    }


@router.post("/resend-otp")
async def resend_otp(mobile_number: str, db: AsyncSession = Depends(get_db)):
    """
    API endpoint to resend OTP.
    """
    return await AuthService.resend_otp(db, mobile_number)



@router.post("/set-mpin")
async def set_mpin(mobile_number: str, mpin: str, db: AsyncSession = Depends(get_db)):
    member = await MemberRepo.get_member_by_mobile_number(db, mobile_number)

    hashed_mpin = hash_password(mpin)
    member.mpin = hashed_mpin

    db.add(member)  # Add the member object (optional if it's already tracked)
    await db.commit()  # ✅ Commit changes to save to the DB
    await db.refresh(member)  # ✅ Refresh to get the updated object from DB

    return member
