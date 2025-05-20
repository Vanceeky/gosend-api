import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.member_models import Member
from models.merchant_models import Merchant
from models.community_models import Community
from models.hub_models import Hub

from utils.otp import generate_otp, create_otp_token, send_otp, verify_otp_token
from sqlalchemy.future import select
import logging
from core.security import sign_jwt, verify_password
from utils.responses import json_response
import redis.asyncio as redis

logger = logging.getLogger(__name__)
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

class AuthRepo:

    @staticmethod
    async def initiate_login(db: AsyncSession, mobile_number: str, role: str):
        try:
            if role == "MEMBER":
                stmt = select(Member).filter_by(mobile_number=mobile_number)
            elif role == "MERCHANT":
                stmt = select(Merchant).filter_by(mobile_number=mobile_number)
            elif role == "LEADER":
                stmt = select(Community).filter_by(community_leader=mobile_number)
            elif role == "HUB":
                stmt = select(Hub).filter_by(hub_user=mobile_number)
            else:
                raise HTTPException(status_code=400, detail="Invalid role selected.")

            result = await db.execute(stmt)
            account = result.scalar_one_or_none()

            if not account:
                raise HTTPException(status_code=404, detail=f"{role.capitalize()} not found.")

            otp = generate_otp()
            # Store OTP in Redis
            await redis_client.setex(f"otp:{mobile_number}", 120, otp)

            send_otp(mobile_number, otp)

            return {
                "otp": otp,
                "role": role,
                "message": "OTP has been sent."
            }

        except Exception as e:
            logger.error("Error in initiate_login: %s", e, exc_info=True)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def verify_otp(mobile_number: str, input_otp: str):
        try:
            # Retrieve the stored OTP from Redis
            stored_otp = await redis_client.get(f"otp:{mobile_number}")

            if not stored_otp:
                raise HTTPException(status_code=404, detail="Invalid or expired OTP. Please request a new one.")
            
            # Check if input OTP matches the stored OTP
            if stored_otp != input_otp:
                raise HTTPException(status_code=400, detail="Incorrect OTP. Please try again.")

            # Mark OTP as verified
            await redis_client.setex(f"otp_verified:{mobile_number}", 120, "true")  # 2-minute expiry

            # Delete the OTP since it's no longer needed
            await redis_client.delete(f"otp:{mobile_number}")

            return {
                "status": "success",
                "message": "OTP verified successfully"
            }

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            logger.error("Error in verify_otp: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during OTP verification.")

    @staticmethod
    async def verify_mpin(db: AsyncSession, mobile_number: str, input_mpin: str, role: str):
        try:
            # Check if OTP verification flag exists
            otp_verified = await redis_client.get(f"otp_verified:{mobile_number}")

            if not otp_verified:
                raise HTTPException(status_code=401, detail="OTP verification required before MPIN verification.")

            # Validate the role and fetch the account
            if role == "MEMBER":
                stmt = select(Member).filter_by(mobile_number=mobile_number)
                user_id_field = "member_id"
            elif role == "MERCHANT":
                stmt = select(Merchant).filter_by(mobile_number=mobile_number)
                user_id_field = "merchant_id"

            elif role == "LEADER":
                stmt = select(Community).filter_by(community_leader=mobile_number)
                user_id_field = "community_id"

            elif role == "HUB":
                stmt = select(Hub).filter_by(hub_user=mobile_number)
                user_id_field = "id"
            else:
                raise HTTPException(status_code=400, detail="Invalid role. Please select MEMBER or MERCHANT.")

            result = await db.execute(stmt)
            account = result.scalar_one_or_none()

            if not account:
                raise HTTPException(status_code=404, detail=f"{role.capitalize()} not found.")

            # Special check for MERCHANT role to validate against MEMBER MPIN
            if role == "MERCHANT" or role == "LEADER" or role == "MEMBER" or role == "HUB":
                member_stmt = select(Member).filter_by(mobile_number=mobile_number)
                member_result = await db.execute(member_stmt)
                member_account = member_result.scalar_one_or_none()
                member_user_id = member_account.member_id

                if not member_account or not verify_password(input_mpin, member_account.mpin):
                    raise HTTPException(status_code=401, detail="Incorrect MPIN.")
            
            else:
                # Validate MPIN for MEMBER role
                if not verify_password(input_mpin, account.mpin):
                    raise HTTPException(status_code=401, detail="Incorrect MPIN.")

            # Generate JWT token
            user_id = str(getattr(account, user_id_field))
            token = sign_jwt(user_id, role, member_user_id)

            # Remove OTP verification flag to prevent reuse
            await redis_client.delete(f"otp_verified:{mobile_number}")

            return {"message": "Login successful", "access_token": token, "role": role, "member_user_id": member_user_id}

        except HTTPException as http_err:
            raise http_err  # Re-raise known HTTP exceptions
        except Exception as e:
            logger.error("Error in verify_mpin: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during MPIN verification.")



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

