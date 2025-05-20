import os
import aiohttp
import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses import json_response
from api.v1.schemas.admin_schemas import ProcessActivation
from api.v1.schemas.topwallet_schemas import P2PTransferRequest, P2PprocessRequest, TWP2PTransferRequest


from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Retrieve configuration from environment variables
TW_API_URL = os.getenv('TW_API_URL')
TW_API_KEY = os.getenv("TW_API_KEY")
TW_SECRET_KEY = os.getenv("TW_SECRET_KEY")
MOTHERWALLET = os.getenv("TW_MOTHERWALLET")




class TopWallet:
    @staticmethod
    async def call_topwallet_api(endpoint: str, payload: dict, method: str = "POST") -> dict:
        """
        Reusable function to call TopWallet API using aiohttp.

        :param endpoint: API endpoint to call, e.g., "b2bapi/user_on_board"
        :param payload: JSON payload to send
        :param method: HTTP method to use ("post" or "get")
        :return: Parsed JSON response from TopWallet API
        :raises HTTPException: if the API call fails or returns a non-200 status code.
        """
        if not TW_API_URL or not TW_API_KEY or not TW_SECRET_KEY:
            logger.error("TopWallet configuration is missing.")
            raise HTTPException(status_code=500, detail=f"TopWallet configuration error")

        url = f"{TW_API_URL}/{endpoint}"
        headers = {
            "apikey": TW_API_KEY,
            "secretkey": TW_SECRET_KEY,
        }
        
        async with aiohttp.ClientSession() as session:
            if method.lower() == "post":
                async with session.post(url, json=payload, headers=headers) as response:
                    status = response.status
                    response_text = await response.text()
                    if status != 200:
                        logger.error("TopWallet API request failed with status %s: %s", status, response_text)
                        raise HTTPException(status_code=status, detail=response_text)
                        #try:
                        #    response_data = await response.json()
                        #except Exception:
                        #    response_data = {}
                        #raise HTTPException(status_code=status, detail=response_data)
                    try:
                        return await response.json()
                    except Exception as e:
                        logger.error("Error parsing TopWallet API response: %s", e, exc_info=True)
                        raise HTTPException(status_code=500, detail="Error parsing TopWallet API response")
            elif method.lower() == "get":
                async with session.get(url, params=payload, headers=headers) as response:
                    status = response.status
                    response_text = await response.text()
                    if status != 200:
                        logger.error("TopWallet API request failed with status %s: %s", status, response_text)
                        try:
                            response_data = await response.json()
                        except Exception:
                            response_data = {}
                        raise HTTPException(status_code=status, detail=response_data)
                    try:
                        return await response.json()
                    except Exception as e:
                        logger.error("Error parsing TopWallet API response: %s", e, exc_info=True)
                        raise HTTPException(status_code=500, detail="Error parsing TopWallet API response")
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            


    # Example usage in your FastAPI endpoint or service:
    @staticmethod
    async def onboard_user_to_topwallet(db: AsyncSession, details_data: dict, user_data: dict, address_data: dict):
        payload = {
            "member_name": f"{details_data['first_name']} {details_data['middle_name']} {details_data['last_name']} {details_data['suffix_name']}",
            "phone": user_data["mobile_number"],
            "member_email": "gosend@gosend.com",
            "dob": "01/01/2000",
            "address": {
                "region": address_data["region"],
                "province": address_data["province"],
                "city": address_data["city"],
                "houseno": address_data["house_number"],
                "barangay": address_data["barangay"],
                "user_politician": address_data.get("user_politician", "false"),
                "user_familymember_politician": address_data.get("user_familymember_politician", "false"),
            },
        }

        print("Payloaad", payload)
        try:
            response_data = await TopWallet.call_topwallet_api("b2bapi/user_on_board", payload, method="POST")

        except HTTPException as e:
            await db.rollback()
            raise HTTPException(status_code=e.status_code, detail=f"Failed to onboard user to TopWallet: {str(e.detail)}")

        except Exception as e:
            await db.rollback()
            logger.error("Unexpected error while onboarding user", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


        external_id = response_data.get("userid")
        if not external_id:
            raise HTTPException(status_code=400, detail="External ID not received from TopWallet")
        
        return external_id



    @staticmethod
    async def verify_kyc(external_id: str):
        payload = {
            # change this to react success page then fetch the kyc verified api
            "return_url": "http://localhost:5173/login",
            "display_name": "GoSEND"
        }

        try:
            response_data = await TopWallet.call_topwallet_api(f"b2bapi/user_kyc_by_id/{external_id}", payload, method="POST")
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"Failed to verify KYC: {str(e.detail)}")
        except Exception as e:
            logger.error("Unexpected error while verifying KYC", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

        return response_data



    @staticmethod
    async def initiate_p2p_transfer(request: P2PTransferRequest) -> dict:
        """
        Initiates a peer-to-peer (P2P) transfer using the TopWallet API.

        :param request: P2PTransferRequest schema containing transfer details
        :return: Parsed JSON response from TopWallet API
        :raises HTTPException: if the API call fails or returns a non-200 status code.
        """
        payload = request.model_dump()
        
        return await TopWallet.call_topwallet_api("b2bapi/initiate_p2ptransfer", payload, "POST")

    @staticmethod
    async def process_p2p_transfer(request: P2PprocessRequest) -> dict:
        """
        Process a peer-to-peer (P2P) transfer using the TopWallet API.

        :param request: P2PTransferRequest schema containing transfer details
        :return: Parsed JSON response from TopWallet API
        :raises HTTPException: if the API call fails or returns a non-200 status code.
        """
        payload = request.model_dump()
        
        return await TopWallet.call_topwallet_api("b2bapi/process_p2ptransfer", payload, "POST")


    @staticmethod
    async def get_user_balance(db: AsyncSession, member_id: str):
        from api.v1.repo.member_repo import MemberRepo

        try:
            external_id = await MemberRepo.get_external_id(db, member_id)
            payload = {
                "userid": external_id
            }
            print("tw_external_id", external_id)
            response_data = await TopWallet.call_topwallet_api(f"b2bapi/get_profile/", payload, method="POST")
            print("response_data_tww", response_data)
            return response_data.get("Balances", {}).get("peso", "0")
        
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"Failed to get user balance: {str(e.detail)}")
        except Exception as e:
            logger.error("Unexpected error while getting user balance", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
        

    @staticmethod
    async def initiate_member_activation(db: AsyncSession, activated_by: str):
        from api.v1.repo.member_repo import MemberRepo

        try:
            external_id = await MemberRepo.get_external_id(db, activated_by)
            print("test_external_id", external_id)
            wallet = await TopWallet.get_balance_by_userid(db, activated_by)
            wallet_balance = wallet['peso']
            print("Wallet chuchu", wallet_balance)

            activation_amount = 10

            print("motherwallet", MOTHERWALLET)

            if float(wallet_balance) < activation_amount:
                return json_response(
                    message="Insufficient balance for activation",
                    data={
                        "current_balance": float(wallet_balance),  # Convert Decimal to float here
                        "required_balance": activation_amount
                    },
                    status_code=400
                )

            
            payload = {
                "from_user": str(external_id),
                "to_user": str(MOTHERWALLET),
                "amount": float(activation_amount),
                "coin": "peso"
            }
            response_data = await TopWallet.call_topwallet_api(f"b2bapi/initiate_p2ptransfer", payload, method="POST")

            return response_data
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"Failed to initiate member activation: {str(e.detail)}")
        except Exception as e:
            logger.error("Unexpected error while initiating member activation", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


    @staticmethod
    async def process_member_activation(activation_data: ProcessActivation):
        try:

            print("test_t_id", activation_data.Transaction_id)
            print("test_member_id", activation_data.member_id)

            payload = {
                "Transaction_id": activation_data.Transaction_id,
                "otp": activation_data.otp_code
            }

            print("payload_test", payload)

            response_data = await TopWallet.call_topwallet_api(
                f"b2bapi/process_p2ptransfer", payload, method="POST"
            )
            
            print("response_dataa", response_data)
            
            return response_data

        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"Failed to process member activation: {str(e.detail)}")
        except Exception as e:
            logger.error("Unexpected error while processing member activation", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")




    @staticmethod
    async def get_banks_list():
        payload = {}
        return await TopWallet.call_topwallet_api("b2bapi/get_banks_list", payload, "POST")

    @staticmethod
    async def cashin_bank_by_id(user_id: str):
        payload = {
            "userid": user_id
        }
        return await TopWallet.call_topwallet_api("b2bapi/cashin_bank_by_id", payload, "POST")

    @staticmethod
    async def get_profile(user_id: str):
        payload = {
            "userid": user_id
        }
        return await TopWallet.call_topwallet_api("b2bapi/get_profile", payload, "POST")

    @staticmethod
    async def generate_qr(user_id: str):
        payload = {
            "userid": user_id
        }

        return await TopWallet.call_topwallet_api('b2bapi/generate_qr', payload, "POST")
    
    @staticmethod
    async def get_balance_by_userid(db: AsyncSession, member_id: str):
        from api.v1.repo.member_repo import MemberRepo

        try:
            external_id = await MemberRepo.get_external_id(db, member_id)

            payload = {
                "userid": external_id
            }

            return await TopWallet.call_topwallet_api('b2bapi/get_balance_by_userid', payload, "POST")

        except Exception as e:
            raise e
        


    @staticmethod
    async def p2p_transfer(db: AsyncSession, data: TWP2PTransferRequest,member_id: str):
        from api.v1.repo.member_repo import MemberRepo

        member_external_id = await MemberRepo.get_external_id(db, member_id)
        to_user = await MemberRepo.get_member_by_mobile_number(db, data.to_user)

        if not to_user:
            raise ValueError("Recipient not found.")

        to_user_external_id = await MemberRepo.get_external_id(db, to_user.member_id)

        payload = {
            "from_user": member_external_id,
            "to_user": to_user_external_id,
            "amount": str(data.amount),
            "coin": data.coin
        }

        return await TopWallet.call_topwallet_api("b2bapi/initiate_p2ptransfer", payload, "POST")
    

    @staticmethod
    async def process_transfer_p2p(data: P2PprocessRequest):
        return await TopWallet.process_p2p_transfer(data)
