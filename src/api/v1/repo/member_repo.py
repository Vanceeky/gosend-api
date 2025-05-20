from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from models.member_models import Member, MemberDetails, MemberAddress, MemberWallet, MemberWalletExtension
from models.wallet_models import Wallet
from models.referral_models import Referral
from models.community_models import Community
from models.merchant_models import Merchant, MerchantDetails, MerchantPurchaseHistory

from api.v1.schemas.member_schemas import MemberCreateSchema
from sqlalchemy.sql import text

from api.v1.repo.wallet_repo import WalletRepository
from fastapi import HTTPException

from api.v1.services.TopWallet import TopWallet
from utils.responses import json_response

from sqlalchemy.exc import IntegrityError
from typing import Optional



from core.security import hash_password

import os
from dotenv import load_dotenv
load_dotenv()

#ADMIN_STAGING = os.getenv("ADMIN_STAGING")
ADMIN_STAGING = '53593d0e-93f8-45b3-9786-55137c4747a8'

from uuid import uuid4
import traceback
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class MemberRepo:


    @staticmethod
    async def create_member(db: AsyncSession, member_data: MemberCreateSchema, referral_id: str = None, external_id: str = None):
 
        try:
            logger.debug("Starting member creation process.")

            # Check if mobile number already exists
            result = await db.execute(select(Member).filter_by(mobile_number=member_data.mobile_number))
            if result.scalars().first():
                logger.warning("Mobile number already used!: %s", member_data.mobile_number)
                raise ValueError("Mobile number already used!")
            
            # Validate Referral ID
            referrer = await MemberRepo.get_member_by_referral_code(db, referral_id)
            if not referrer:
                logger.warning("Invalid referral ID: %s", referral_id)
                raise HTTPException(status_code=400, detail="Invalid referral ID.")

            if not referrer.is_activated:
                logger.warning("Referrer is not activated: %s", referrer.mobile_number)
                raise HTTPException(status_code=400, detail="Referrer is not activated.")
            

            # Create new Member instance
            new_member = Member(
                member_id=str(uuid4()),
                mobile_number=member_data.mobile_number,
                mpin = hash_password('1234'),
                account_type=member_data.account_type,
                is_kyc_verified = True,
                referral_id=str(uuid4())[:12],
                community_id = referrer.community_id
            )
            logger.debug("New member created with ID: %s", new_member.member_id)

            # Create Member Details
            member_details = MemberDetails(
                member_id=new_member.member_id,
                first_name=member_data.details.first_name.upper() if member_data.details.first_name else None,
                last_name=member_data.details.last_name.upper() if member_data.details.last_name else None,
                middle_name=member_data.details.middle_name.upper() if member_data.details.middle_name else None,
                suffix_name=member_data.details.suffix_name.upper() if member_data.details.suffix_name else None,
            )
            logger.debug("Member details created for member ID: %s", new_member.member_id)

            # Create Member Address
            member_address = MemberAddress(
                member_id=new_member.member_id,
                house_number=member_data.address.house_number.upper() if member_data.address.house_number else None,
                street_name=member_data.address.street_name.upper() if member_data.address.street_name else None,
                barangay=member_data.address.barangay.upper() if member_data.address.barangay else None,
                city=member_data.address.city.upper() if member_data.address.city else None,
                province=member_data.address.province.upper() if member_data.address.province else None,
                region=member_data.address.region.upper() if member_data.address.region else None,
            )
            logger.debug("Member address created for member ID: %s", new_member.member_id)

            # Create Wallet and MemberWallet
            new_wallet = Wallet(
                wallet_id=str(uuid4()),
                public_address=str(uuid4()),  # Generate unique wallet address
            )
            logger.debug("New wallet created with ID: %s", new_wallet.wallet_id)

            member_wallet = MemberWallet(
                wallet_id=new_wallet.wallet_id,
                member_id=new_member.member_id,
                is_primary=True
            )
            logger.debug("Member wallet association created for member ID: %s", new_member.member_id)

            # Retrieve wallet extension info
            extension_name = "TopWallet"
            user_wallet_extension = await WalletRepository.get_wallet_extension(db, extension_name)
            extension_id = user_wallet_extension.wallet_extension_id

            member_wallet_extension = MemberWalletExtension(
                member_wallet_extension_id=str(uuid4()),
                extension_id=extension_id,
                wallet_id=new_wallet.wallet_id,
                external_id = external_id
            )
            logger.debug("Member wallet extension created for wallet ID: %s", new_wallet.wallet_id)

            refferal = Referral(
                referred_by = referrer.member_id,
                referred_member = new_member.member_id
            )
            # Add all objects to the session
            db.add(new_member)
            db.add(member_details)
            db.add(member_address)
            db.add(new_wallet)
            db.add(member_wallet)
            db.add(member_wallet_extension)
            db.add(refferal)

            # Commit transaction
            await db.commit()
            logger.info("Member creation transaction committed for member ID: %s", new_member.member_id)

            # Attempt to refresh new_member from the database.
            try:
                await db.refresh(new_member)
                logger.debug("Member refreshed successfully for member ID: %s", new_member.member_id)
            except Exception as refresh_err:
                logger.error("Error refreshing new_member: %s", refresh_err, exc_info=True)
                # Optionally, you can decide to pass or re-raise the error if needed.
            
            return new_member

        except Exception as e:
            logger.error("Error occurred during member creation: %s", e, exc_info=True)
            traceback.print_exc()  # Prints the full error details
            raise HTTPException(detail=str(e), status_code=500)
        

    @staticmethod
    async def get_member(db: AsyncSession, member_id: str):
        # Query to fetch a single member with their details, address, and wallet
        query = (
            select(
                Member.member_id.label("user_id"),
                Member.mobile_number,
                Member.is_activated.label("status"),
                Member.referral_id,
                Member.account_type,
                Member.is_kyc_verified,
                Member.created_at,
                Member.updated_at,
                MemberDetails.first_name,
                MemberDetails.middle_name,
                MemberDetails.last_name,
                MemberDetails.suffix_name,
                MemberAddress.house_number,
                MemberAddress.street_name,
                MemberAddress.barangay,
                MemberAddress.city,
                MemberAddress.province,
                MemberAddress.region,
                Wallet.wallet_balance,
                Wallet.reward_points
            )
            .join(MemberDetails, Member.member_id == MemberDetails.member_id, isouter=True)
            .join(MemberAddress, Member.member_id == MemberAddress.member_id, isouter=True)
            .join(MemberWallet, Member.member_id == MemberWallet.member_id, isouter=True)
            .join(Wallet, MemberWallet.wallet_id == Wallet.wallet_id, isouter=True)
            .where(Member.member_id == member_id)
        )

        result = await db.execute(query)
        member = result.fetchone()
        if not member:
            return None

        return member


    @staticmethod
    async def get_member_by_referral_code(db: AsyncSession, referral_id: str):
        
        try:
            stmt = select(Member).filter_by(referral_id=referral_id)
            
            result = await db.execute(stmt)
            member = result.scalar_one_or_none()  # Efficient alternative to scalars().first()
            
            if not member:
                raise HTTPException(status_code=404, detail="Referrer not found.")
            
            return member
        
        except Exception as e:
            logger.error("Error occurred during member creation: %s", e, exc_info=True)
            traceback.print_exc()  # Prints the full error details
            raise HTTPException(detail=str(e), status_code=500)
        
    async def get_member_by_mobile_number(db: AsyncSession, mobile_number: str):
        try:
            stmt = select(Member).where(Member.mobile_number == mobile_number)
            
            result = await db.execute(stmt)
            member = result.scalar_one_or_none() 
            
            if not member:
                raise HTTPException(status_code=404, detail="Member not found.")
            
            return member

        except Exception as e:
            logger.error("Error occurred getting member: %s", e, exc_info=True)
            traceback.print_exc()  # Prints the full error details
            raise HTTPException(detail=str(e), status_code=500)
        
    async def get_member_by_id(db: AsyncSession, member_id: str):
        try:
            stmt = select(Member).filter_by(member_id=member_id)
            
            result = await db.execute(stmt)
            member = result.scalar_one_or_none() 
            
            if not member:
                raise HTTPException(status_code=404, detail="Member not found.")
            
            return member

        except Exception as e:
            logger.error("Error occurred getting member: %s", e, exc_info=True)
            traceback.print_exc()  # Prints the full error details
            raise HTTPException(detail=str(e), status_code=500)
        

    async def get_external_id(db: AsyncSession, member_id: str):
        query = (
            select(MemberWalletExtension.external_id)
            .join(MemberWallet, MemberWalletExtension.wallet_id == MemberWallet.wallet_id)
            .where(MemberWallet.member_id == member_id)
        )
        result = await db.execute(query)
        external_id = result.scalar_one_or_none()
        
        if not external_id:
            raise HTTPException(status_code=404, detail="External ID not found")
        
        return external_id


    @staticmethod
    async def get_reward_points(db: AsyncSession, member_id: str):
        query = select(Wallet.reward_points).join(MemberWallet).where(MemberWallet.member_id == member_id)
        result = await db.execute(query)
        reward_points = result.scalar()

        return reward_points if reward_points is not None else 0.0
    
    @staticmethod
    async def get_all_members(db: AsyncSession, is_activated: Optional[bool] = None):
        query = (
            select(
                Member.member_id.label("user_id"),
                Member.mobile_number,
                Member.is_activated.label("status"),
                Member.created_at,
                Member.updated_at,
                Member.is_activated,
                Member.is_kyc_verified,
                Member.community_id,
                MemberDetails.first_name,
                MemberDetails.middle_name,
                MemberDetails.last_name,
                MemberDetails.suffix_name,
                MemberAddress.house_number,
                MemberAddress.street_name,
                MemberAddress.barangay,
                MemberAddress.city,
                MemberAddress.province,
                MemberAddress.region,
                Wallet.wallet_balance,
                Wallet.reward_points,
                Community.community_name
            )
            .join(MemberDetails, Member.member_id == MemberDetails.member_id, isouter=True)
            .join(MemberAddress, Member.member_id == MemberAddress.member_id, isouter=True)
            .join(MemberWallet, Member.member_id == MemberWallet.member_id, isouter=True)
            .join(Wallet, MemberWallet.wallet_id == Wallet.wallet_id, isouter=True)
            .join(Community, Member.community_id == Community.community_id, isouter=True)  # Added join to Community
        )

        # Apply filtering if is_activated is provided
        if is_activated is not None:
            query = query.where(Member.is_activated == is_activated)

        result = await db.execute(query)
        members = result.all()
        return members


    # REFERALLS
    
    @staticmethod
    async def get_member_referrer(db: AsyncSession, member_id: str):
        query = select(Referral.referred_by).where(Referral.referred_member == member_id).limit(1)
        result = await db.execute(query)
        referrer = result.scalar()

        return referrer  # Returns None if no referrer is found


    @staticmethod
    async def get_member_unilevel(db: AsyncSession, member_id: str):
        try:
            query = text("""
                WITH RECURSIVE unilevel AS (
                    SELECT referred_by, referred_member, 1 AS level
                    FROM referrals
                    WHERE referred_member = :member_id
                    UNION ALL
                    SELECT r.referred_by, r.referred_member, u.level + 1
                    FROM referrals r
                    JOIN unilevel u ON r.referred_member = u.referred_by
                    WHERE u.level < 3  -- Limit to 3 levels
                )
                SELECT referred_by, level FROM unilevel ORDER BY level
            """)
            result = await db.execute(query, {"member_id": member_id})
            rows = result.fetchall()

            # Default values
            levels = {
                "first_level": ADMIN_STAGING,
                "second_level": ADMIN_STAGING,
                "third_level": ADMIN_STAGING
            }

            # Assign fetched values
            for row in rows:
                if row.level == 1:
                    levels["first_level"] = row.referred_by
                elif row.level == 2:
                    levels["second_level"] = row.referred_by
                elif row.level == 3:
                    levels["third_level"] = row.referred_by

            return levels

        except Exception as e:
            logger.error("Error occurred getting member unilevel: %s", e, exc_info=True)
            traceback.print_exc()
            raise HTTPException(detail=str(e), status_code=500)
    

    @staticmethod
    async def get_member_unilevel_5(db: AsyncSession, member_id: str):
        try:
            query = text("""
                WITH RECURSIVE unilevel AS (
                    SELECT referred_by, referred_member, 1 AS level
                    FROM referrals
                    WHERE referred_member = :member_id
                    UNION ALL
                    SELECT r.referred_by, r.referred_member, u.level + 1
                    FROM referrals r
                    JOIN unilevel u ON r.referred_member = u.referred_by
                    WHERE u.level < 5  -- Limit to 5 levels
                )
                SELECT referred_by, level FROM unilevel ORDER BY level
            """)
            result = await db.execute(query, {"member_id": member_id})
            rows = result.fetchall()

            # Default values
            levels = {
                "first_level": ADMIN_STAGING,
                "second_level": ADMIN_STAGING,
                "third_level": ADMIN_STAGING,
                "forth_level": ADMIN_STAGING,
                "fifth_level": ADMIN_STAGING
            }

            # Assign fetched values
            for row in rows:
                if row.level == 1:
                    levels["first_level"] = row.referred_by
                elif row.level == 2:
                    levels["second_level"] = row.referred_by
                elif row.level == 3:
                    levels["third_level"] = row.referred_by
                elif row.level == 4:
                    levels["forth_level"] = row.referred_by
                elif row.level == 5:
                    levels["fifth_level"] = row.referred_by

            return levels

        except Exception as e:
            logger.error("Error occurred getting member unilevel: %s", e, exc_info=True)
            traceback.print_exc()
            raise HTTPException(detail=str(e), status_code=500)




    @staticmethod
    async def get_member_unilevel_main(db: AsyncSession, member_id: str):
        try:
            first_level = await MemberRepo.get_member_referrer(db, member_id) or ADMIN_STAGING
            second_level = await MemberRepo.get_member_referrer(db, first_level) or ADMIN_STAGING
            third_level = await MemberRepo.get_member_referrer(db, second_level) or ADMIN_STAGING

            return {
                "first_level": first_level,
                "second_level": second_level,
                "third_level": third_level,
            }

        except Exception as e:
            logger.error("Error occurred getting member unilevel: %s", e, exc_info=True)
            traceback.print_exc()
            raise HTTPException(detail=str(e), status_code=500)


    @staticmethod
    async def get_member_unilevel_5_main(db: AsyncSession, member_id: str):
        try:
            first_level = await MemberRepo.get_member_referrer(db, member_id)
            if not first_level:
                return {
                    "first_level": ADMIN_STAGING, 
                    "second_level": ADMIN_STAGING, 
                    "third_level": ADMIN_STAGING,
                    "forth_level": ADMIN_STAGING,
                    "fifth_level": ADMIN_STAGING
                }

            second_level = await MemberRepo.get_member_referrer(db, first_level) or ADMIN_STAGING
            third_level = await MemberRepo.get_member_referrer(db, second_level) or ADMIN_STAGING
            forth_level = await MemberRepo.get_member_referrer(db, third_level) or ADMIN_STAGING
            fifth_level = await MemberRepo.get_member_referrer(db, forth_level) or ADMIN_STAGING

            return {
                "first_level": first_level,
                "second_level": second_level,
                "third_level": third_level,
                "forth_level": forth_level,
                "fifth_level": fifth_level
            }

        except Exception as e:
            logger.error("Error occurred getting member: %s", e, exc_info=True)
            traceback.print_exc()
            raise HTTPException(detail=str(e), status_code=500)



    @staticmethod
    async def get_member_purchase_history(db: AsyncSession, member_id: str):
        """
        Fetch all purchase history records for a specific member.
        
        :param session: AsyncSession - Database session
        :param member_id: str - ID of the member
        :return: List of purchase history records with merchant business name, amount, status, and created_at
        """
        query = (
            select(
                MerchantPurchaseHistory.purchase_id,
                Merchant.business_name,
                MerchantPurchaseHistory.amount,
                MerchantPurchaseHistory.reference_id,
                MerchantPurchaseHistory.status,
                MerchantPurchaseHistory.created_at
            )
            .join(Merchant, Merchant.merchant_id == MerchantPurchaseHistory.merchant_id)
            .filter(MerchantPurchaseHistory.member_id == member_id)
            .order_by(MerchantPurchaseHistory.created_at.desc())
        )
        result = await db.execute(query)
        return result.all()