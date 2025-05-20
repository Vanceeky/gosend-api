from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.v1.schemas.merchant_schemas import MerchantCreate, MerchantResponse, PayQR, ProcessPay, MerchantPurchaseCreate
from api.v1.schemas.topwallet_schemas import P2PTransferRequest, P2PprocessRequest

from utils.responses import json_response

from fastapi import HTTPException

from api.v1.repo.merchant_repo import MerchantRepo
from api.v1.repo.member_repo import MemberRepo
from api.v1.services.TopWallet import TopWallet


from api.v1.services.reward_services import RewardService
from decimal import Decimal

import os
from dotenv import load_dotenv
load_dotenv()


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

MOTHERWALLET = os.getenv("TW_MOTHERWALLET")


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
        


    @staticmethod
    async def pay_qr(db: AsyncSession, qr_data: PayQR, member_id: str):
        try:

            customer = await MemberRepo.get_member_by_id(db, member_id)
            merchant = await MerchantRepo.get_merchant_by_id(db, qr_data.merchant_id)

            target_url = (
                f"https://gosendit.net/paynow.php?"
                f"user_id={customer.member_id}&"
                f"merchant_id={merchant.get('merchant_id')}&"
                f"amount={qr_data.amount}"
            )

            return json_response(
                status_code = 200,
                message = "Successfully fetch PayQR URL",
                data = {
                    "url": target_url
                }
            )

        except HTTPException as e:
            raise e
        
        except Exception as e:
            logger.error("Error merchant qr payment: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    async def initiate_pay_merchant(db: AsyncSession, merchant_id: str, member_id: str, data: PayQR):
        try:
            # Fetch customer external ID
            customer = await MemberRepo.get_external_id(db, member_id)
            print("Customer_external_id", customer)

            # Ensure merchant exists
            await MerchantRepo.get_merchant_by_id(db, merchant_id)



            #merchant = await MerchantRepo.get_merchant_by_id(db, merchant_id)
            #discount = merchant["discount"]
            #discount = float(discount)
            #amount = float(data.amount)

            # calculate the discounted amount
            #reward_pool = amount * (discount / 100) # discount as a percentage
            #merchant_amount = amount - reward_pool # total after discount


            # Prepare transfer request
            transfer_request = P2PTransferRequest(
                from_user=customer,  # Assuming `customer.external_id` exists
                to_user=str(MOTHERWALLET), 
                amount=str(data.amount),
                coin="peso"
            )

            response = await TopWallet.initiate_p2p_transfer(transfer_request)

            return json_response(
                message="Successfully initiated merchant payment",
                data=response,
                status_code=200
            )

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("Error initiating merchant payment: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
        

    @staticmethod
    async def process_pay_merchant(db: AsyncSession, merchant_id: str, member_id: str, data: ProcessPay):

        try:




            transfer_request = P2PprocessRequest(
                Transaction_id=data.Transaction_id,
                otp = data.otp
            )

            response = await TopWallet.process_p2p_transfer(transfer_request)

            # save purchase
            purchase_data = MerchantPurchaseCreate(
                merchant_id=merchant_id,
                member_id=member_id,
                amount=data.amount,
                reference_id=response['success'],
                extra_metadata=None,
                description="Merchant payment",
                status=response['status']
            )
            await MerchantRepo.create_purchase(db, purchase_data)



            return json_response(
                message="Successfully Process merchant payment",
                data=response,
                status_code=200
            )
        
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("Error Processing merchant payment: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
        






