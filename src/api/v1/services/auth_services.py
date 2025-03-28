from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.repo.auth_repo import AuthRepo  # Import the repo layer

class AuthService:
    @staticmethod
    async def login(db: AsyncSession, mobile_number: str, role: str):
        """
        Handles login by verifying mobile number and sending OTP.
        """
        return await AuthRepo.initiate_login(db, mobile_number, role)
    @staticmethod
    async def verify_otp(mobile_number: str, input_otp: str):
        """
        Handles OTP verification.
        """
        return await AuthRepo.verify_otp(mobile_number, input_otp)
    @staticmethod
    async def verify_mpin(db: AsyncSession, mobile_number: str, input_mpin: str, role: str):
        """
        Handles MPIN verification and generates JWT.
        """
        return await AuthRepo.verify_mpin(db, mobile_number, input_mpin, role)

    @staticmethod
    async def resend_otp(db: AsyncSession, mobile_number: str):
        """
        Handles OTP resending.
        """
        return await AuthRepo.resend_otp(db, mobile_number)



