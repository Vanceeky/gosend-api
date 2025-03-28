from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from sqlalchemy import select

from typing import Optional
from api.v1.schemas.member_schemas import MemberCreateSchema, MemberAddressSchema, MemberDetailsSchema, MemberListResponse, WalletResponse, MemberReadSchema, MemberInfoSchema

from api.v1.repo.member_repo import MemberRepo
from utils.responses import json_response

from fastapi import HTTPException

from api.v1.services.TopWallet import TopWallet



import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler() 
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class MemberService:
    @staticmethod
    async def create_member(db: AsyncSession, member_data: MemberCreateSchema, referral_id: str = None):
        try:
            logger.debug("MemberService: Starting create_member service call.")


            # Call the TopWallet onboarding function using data from member_data
            # Adjust the dictionary keys to match your schema
            details_data = {
                "first_name": member_data.details.first_name,
                "middle_name": member_data.details.middle_name,
                "last_name": member_data.details.last_name,
                "suffix_name": member_data.details.suffix_name
            }
            # If email address is part of member_data, otherwise adjust accordingly.
            user_data = {
                "mobile_number": member_data.mobile_number,
            }
            address_data = {
                "region": member_data.address.region,
                "province": member_data.address.province,
                "city": member_data.address.city,
                "house_number": member_data.address.house_number,
                "barangay": member_data.address.barangay,
                "user_politician": getattr(member_data.address, "user_politician", "false"),
                "user_familymember_politician": getattr(member_data.address, "user_familymember_politician", "false"),
            }
            
            print("address_Dataaa", address_data)
            # Call the reusable onboard function
            external_id = await TopWallet.onboard_user_to_topwallet(db, details_data, user_data, address_data)
            if external_id:
                new_member = await MemberRepo.create_member(db, member_data, referral_id, external_id)
                # Fetch KYC details using the external_id
                kyc_response = await TopWallet.verify_kyc(external_id)

            logger.info("TopWallet onboard successful. External ID: %s", external_id)

            logger.info("MemberService: Successfully created member with ID: %s", new_member.member_id)

            # Return response including KYC details
            return json_response(
                status_code=200,
                message="Member created successfully",
                data={
                    "external_id": external_id,
                    "kyc_response": kyc_response  # Extract only KYC data
                }
            )

        except IntegrityError as ie:
            await db.rollback()
            logger.error("IntegrityError during member creation: %s", ie, exc_info=True)
            raise ValueError("Member already exists or invalid data.")

        except Exception as e:
            logger.error("Unhandled exception in MemberService.create_member: %s", e, exc_info=True)
            raise e
        


    
    @staticmethod
    async def get_all_members(db: AsyncSession, is_activated: Optional[bool] = None):
        # Fetch data from the repository with filtering
        members = await MemberRepo.get_all_members(db, is_activated)

        if not members:
            raise HTTPException(status_code=404, detail="No members found")

        formatted_members = [
            MemberListResponse(
                user_id=member.user_id,
                mobile_number=member.mobile_number,
                status=member.status,
                is_activated=member.is_activated,
                is_kyc_verified=member.is_kyc_verified,
                created_at=member.created_at.isoformat(),
                updated_at=member.updated_at.isoformat(),
                community_id = member.community_id,
                community_name=member.community_name,
                user_address=MemberAddressSchema(
                    house_number=member.house_number,
                    street_name=member.street_name,
                    barangay=member.barangay,
                    city=member.city,
                    province=member.province,
                    region=member.region
                ),
                user_details=MemberDetailsSchema(
                    first_name=member.first_name,
                    middle_name=member.middle_name,
                    last_name=member.last_name,
                    suffix_name=member.suffix_name
                ),
                wallet=WalletResponse(
                    wallet_balance=member.wallet_balance if member.wallet_balance else 0.0,
                    reward_points=member.reward_points if member.reward_points else 0.0
                )
            )
            for member in members
        ]

        formatted_members_dict = [member.model_dump() for member in formatted_members]

        return json_response(
            message="Members retrieved successfully",
            status_code=200,
            data=formatted_members_dict
        )
    


    @staticmethod
    async def get_member_by_id(db: AsyncSession, member_id: str):
        try:

            balance = await TopWallet.get_user_balance(db, member_id)
                    
            return balance
           
        except Exception as e:
            logger.error("Error occurred getting member: %s", e, exc_info=True)
            raise HTTPException(detail=str(e), status_code=500)

    @staticmethod
    async def get_member(db: AsyncSession, member_id: str):
        member_data = await MemberRepo.get_member(db, member_id)
        print("testtt", member_data)
        if not member_data:
            return json_response(
                message=f"Member with ID {member_id} not found.",
                status_code=404,
                data={}
            )

        wallet_data = await TopWallet.get_user_balance(db, member_id)

        member_schema = MemberInfoSchema(
            member_id=member_data.user_id,
            mobile_number=member_data.mobile_number,
            is_activated=member_data.status,
            is_kyc_verified=member_data.is_kyc_verified,
            referral_id=member_data.referral_id,
            account_type=member_data.account_type,
            details=MemberDetailsSchema(
                first_name=member_data.first_name,
                middle_name=member_data.middle_name,
                last_name=member_data.last_name,
                suffix_name=member_data.suffix_name
            ) if member_data.first_name else None,
            address=MemberAddressSchema(
                house_number=member_data.house_number,
                street_name=member_data.street_name,
                barangay=member_data.barangay,
                city=member_data.city,
                province=member_data.province,
                region=member_data.region
            ) if member_data.house_number else None,
            wallet=WalletResponse(
                wallet_balance=float(wallet_data),
                reward_points=member_data.reward_points
            ) 
        )

        print("testt", member_schema.dict())

        return json_response(
            message="Member retrieved successfully.",
            status_code=200,
            data=member_schema.dict()
        )
    



