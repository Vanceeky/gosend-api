from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.v1.schemas.merchant_schemas import MerchantCreate, MerchantResponse

from utils.responses import json_response

from fastapi import HTTPException

from api.v1.repo.merchant_repo import MerchantRepo

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class MerchantService:
    @staticmethod
    async def create_merchant(db: AsyncSession, merchant_data: MerchantCreate, referral_id: str):
        logger.info("Creating new merchant with mobile number: %s", merchant_data.mobile_number)
        
        result = await MerchantRepo.create_merchant(db, merchant_data, referral_id)
        
        if result["status_code"] == 200:
            logger.info("Merchant created successfully: %s", result["data"]["merchant_id"])
        elif result["status_code"] == 400:
            logger.warning("Failed to create merchant: %s", result["message"])
        else:
            logger.error("Unexpected error during merchant creation")

        return json_response(
            status_code=result['status_code'],
            message = result['message'],
            data = result['data']
        )
    @staticmethod
    async def get_merchant(db: AsyncSession, merchant_id: str):
        try:
            merchant_data = await MerchantRepo.get_merchant_by_id(db, merchant_id)
            if not merchant_data:
                raise HTTPException(status_code=404, detail="Merchant not found")
            return {
                "status": "success",
                "message": "Merchant retrieved successfully",
                "data": merchant_data
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        

    @staticmethod
    async def get_all_merchants(db: AsyncSession):
        try:
            merchant_list = await MerchantRepo.get_all_merchants(db)

            return json_response(
                status_code=200,
                message="Merchants retrieved successfully.",
                data=merchant_list
            )

        except Exception as e:
            logger.error("Error retrieving merchants: %s", str(e))
            return json_response(
                status_code=500,
                message="An error occurred while fetching merchants.",
                data=None
            )
        
    @staticmethod
    async def get_merchant_purchase_history(db: AsyncSession, merchant_id: str):
        try:
            purchases = await MerchantRepo.get_merchant_purchase_history(db, merchant_id)
            return json_response(
                message="Merchant purchase history fetched successfully",
                status_code=200,
                data={"purchases": purchases}
            )
        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500,
                data=None
            )