import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.member_models import Member  # Import your Member model
from models.merchant_models import Merchant
from utils.otp import generate_otp, create_otp_token, send_otp, verify_otp_token  # Import OTP functions
from sqlalchemy.future import select
import logging
from core.security import sign_jwt, verify_password

from utils.responses import json_response

logger = logging.getLogger(__name__)


class AuthRepo:

    @staticmethod
    async def initiate_login(db: AsyncSession, mobile_number: str, role: str):
        """Step 1: Verify mobile number based on role, generate OTP, and send OTP."""
        try:
            # 🔥 Validate role early
            if role == "MEMBER":
                stmt = select(Member).filter_by(mobile_number=mobile_number)
            elif role == "MERCHANT":
                stmt = select(Merchant).filter_by(mobile_number=mobile_number)
            else:
                raise HTTPException(status_code=400, detail="Invalid role selected.")

            # 🔥 Check if the account exists in the correct table
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()

            if not account:
                raise HTTPException(status_code=404, detail=f"{role.capitalize()} not found.")

            # 🔥 Generate OTP
            otp = generate_otp()

            # 🔥 Create OTP token (now includes role!)
            otp_token = create_otp_token(mobile_number, otp, role)

            # 🔥 Send OTP to the user
            send_otp(mobile_number, otp)

            # ✅ Return OTP token and role (frontend will use this in the next step)
            return {
                "otp_token": otp_token,
                "otp": otp,
                "role": role,  # ✅ Add this line
                "message": "OTP has been sent."
            }

        except Exception as e:
            logger.error("Error in initiate_login: %s", e, exc_info=True)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def verify_otp(db: AsyncSession, mobile_number: str, otp_token: str, input_otp: str):
        """
        Step 2: Verify OTP from the token and store validation in Redis.
        """
        try:
            # 🔥 Verify the OTP token and extract data
            otp_data = verify_otp_token(otp_token, input_otp)

            if otp_data == "expired":
                raise HTTPException(status_code=400, detail="OTP has expired.")

            if not otp_data:
                raise HTTPException(status_code=401, detail="Invalid OTP.")

            # 🔥 Ensure the mobile number from the OTP matches the provided mobile_number
            token_mobile_number = otp_data["mobile_number"]
            if token_mobile_number != mobile_number:
                raise HTTPException(status_code=401, detail="Mobile number does not match OTP.")

            # ✅ Store verification status in Redis (Valid for 5 minutes)
            await redis.setex(f"otp_verified:{mobile_number}", 300, "true")

            return {"message": "OTP verified successfully"}

        except Exception as e:
            logger.error("Error in verify_otp: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Error verifying OTP")

    @staticmethod
    async def verify_mpin(db: AsyncSession, mobile_number: str, input_mpin: str, role: str):
        """Step 3: Verify MPIN only if OTP was validated in Redis."""
        try:
            # ✅ Check if OTP was verified in Redis
            otp_verified = await redis.get(f"otp_verified:{mobile_number}")

            if not otp_verified:
                raise HTTPException(status_code=401, detail="OTP verification required before MPIN.")

            if role == "MEMBER":
                stmt = select(Member).filter_by(mobile_number=mobile_number)
                user_id_field = "member_id"
            elif role == "MERCHANT":
                stmt = select(Merchant).filter_by(mobile_number=mobile_number)
                user_id_field = "merchant_id"
            else:
                raise HTTPException(status_code=400, detail="Invalid role selected.")

            result = await db.execute(stmt)
            account = result.scalar_one_or_none()

            if not account:
                raise HTTPException(status_code=404, detail=f"{role.capitalize()} not found.")

            if role == "MERCHANT":
                member_stmt = select(Member).filter_by(mobile_number=mobile_number)
                member_result = await db.execute(member_stmt)
                member_account = member_result.scalar_one_or_none()

                if not member_account:
                    raise HTTPException(status_code=404, detail="Merchant is not registered as a Member.")

                if not verify_password(input_mpin, member_account.mpin):
                    raise HTTPException(status_code=401, detail="Incorrect MPIN.")

            elif role == "MEMBER":
                if not verify_password(input_mpin, account.mpin):
                    raise HTTPException(status_code=401, detail="Incorrect MPIN.")

            user_id = str(getattr(account, user_id_field))
            token = sign_jwt(user_id, role)

            # ✅ Remove OTP verification key from Redis after successful MPIN verification
            await redis.delete(f"otp_verified:{mobile_number}")

            return {"message": "Login successful", "access_token": token, "role": role}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error verifying MPIN: {str(e)}")


    @staticmethod
    async def verify_otp_main(db: AsyncSession, mobile_number: str, otp_token: str, input_otp: str):
        """
        Step 2: Verify OTP from the token.
        """
        try:
            # 🔥 Verify the OTP token and extract data
            otp_data = verify_otp_token(otp_token, input_otp)

            if otp_data == "expired":
                raise HTTPException(status_code=400, detail="OTP has expired.")

            if not otp_data:
                raise HTTPException(status_code=401, detail="Invalid OTP.")

            # 🔥 Ensure the mobile number from the OTP matches the provided mobile_number
            token_mobile_number = otp_data["mobile_number"]
            if token_mobile_number != mobile_number:
                raise HTTPException(status_code=401, detail="Mobile number does not match OTP.")

            return {"message": "OTP verified successfully"}

        except Exception as e:
            logger.error("Error in verify_otp: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Error verifying OTP")

    @staticmethod
    async def verify_mpin_main(db: AsyncSession, mobile_number: str, input_mpin: str, role: str):
        """Step 3: Verify MPIN and return JWT token with correct role and user ID."""
        try:
            if role == "MEMBER":
                # 🔥 Query Member directly
                stmt = select(Member).filter_by(mobile_number=mobile_number)
                user_id_field = "member_id"

            elif role == "MERCHANT":
                # 🔥 Query Merchant first
                stmt = select(Merchant).filter_by(mobile_number=mobile_number)
                user_id_field = "merchant_id"

            else:
                raise HTTPException(status_code=400, detail="Invalid role selected.")

            # 🔥 Execute query for Merchant or Member
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()

            if not account:
                raise HTTPException(status_code=404, detail=f"{role.capitalize()} not found.")

            # 🔥 If Merchant, check the Member record for MPIN
            if role == "MERCHANT":
                member_stmt = select(Member).filter_by(mobile_number=mobile_number)
                member_result = await db.execute(member_stmt)
                member_account = member_result.scalar_one_or_none()

                if not member_account:
                    raise HTTPException(status_code=404, detail="Merchant is not registered as a Member.")

                # 🔥 Verify MPIN using Member's MPIN
                if not verify_password(input_mpin, member_account.mpin):
                    raise HTTPException(status_code=401, detail="Incorrect MPIN.")

            # 🔥 If Member, verify MPIN normally
            elif role == "MEMBER":
                if not verify_password(input_mpin, account.mpin):
                    raise HTTPException(status_code=401, detail="Incorrect MPIN.")

            # 🔥 Determine correct ID to store in the token
            user_id = str(getattr(account, user_id_field))

            # 🔥 Generate JWT Token
            token = sign_jwt(user_id, role)

            
            return {"message": "Login successful", "access_token": token, "role": role}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error verifying MPIN: {str(e)}")



    @staticmethod
    async def resend_otp(db: AsyncSession, mobile_number: str):
        """
        Step 3: Resend OTP by generating a new OTP and sending it.
        """
        try:
            # Check if the mobile number exists
            stmt = select(Member).filter_by(mobile_number=mobile_number)
            result = await db.execute(stmt)
            member = result.scalar_one_or_none()

            if not member:
                raise HTTPException(status_code=404, detail="Member not found.")

            # Generate a new OTP
            new_otp = generate_otp()

            # Create a new OTP token
            new_otp_token = create_otp_token(mobile_number, new_otp)

            # Send the new OTP to the user
            send_otp(mobile_number, new_otp)

            return {"otp_token": new_otp_token, "otp": new_otp, "message": "New OTP has been sent."}

        except Exception as e:
            logger.error("Error in resend_otp: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Error resending OTP")



