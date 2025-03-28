from sqlalchemy.ext.asyncio import AsyncSession
from models.merchant_models import Merchant, MerchantDetails, MerchantReferral, MerchantPurchaseHistory
from api.v1.schemas.merchant_schemas import MerchantCreate
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from api.v1.repo.member_repo import MemberRepo

from models.member_models import Member, MemberDetails

from fastapi import HTTPException

from models.member_models import Member


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class MerchantRepo:
    @staticmethod
    async def create_merchant(db: AsyncSession, merchant_data: MerchantCreate, referral_id: str):
        try:

            # Try to get the referrer
            try:
                await MemberRepo.get_member_by_referral_code(db, referral_id)
            except HTTPException as e:
                logger.warning("Invalid referral ID: %s", referral_id)
                return {
                    "status_code": 400,  # Change this to 400 instead of 500
                    "message": "Invalid Referral ID.",
                    "data": None
                }
            
            try:
                member = await MemberRepo.get_member_by_mobile_number(db, merchant_data.mobile_number)
                
            except HTTPException as e:
                logger.warning("Mobile number is not registered: %s", merchant_data.mobile_number)
                return {
                    "status_code": 400,  # Change this to 400 instead of 500
                    "message": f"Mobile number is not registered!",
                    "data": None
                }
            # Check if mobile number already exists
            stmt = select(Merchant).where(Merchant.mobile_number == merchant_data.mobile_number)
            result = await db.execute(stmt)
            existing_merchant = result.scalar_one_or_none()

            if existing_merchant:
                logger.warning("Merchant with mobile number %s already exists.", merchant_data.mobile_number)
                return {
                    "status_code": 400,
                    "message": "Merchant already registered.",
                    "data": None
                }

            merchant_id = str(uuid4())

            # Create new merchant record
            new_merchant = Merchant(
                merchant_id=merchant_id,
                mobile_number=merchant_data.mobile_number,
                business_name=merchant_data.business_name,
                business_type=merchant_data.business_type,
                discount=merchant_data.discount,
                merchant_wallet=merchant_data.merchant_wallet,
                reward_points=merchant_data.reward_points,
                #qr_code_url=merchant_data.qr_code_url
            )
            db.add(new_merchant)

            # Create merchant details record
            merchant_details = MerchantDetails(
                merchant_id=merchant_id,
                latitude=merchant_data.latitude,
                longitude=merchant_data.longitude,
                region=merchant_data.region,
                province=merchant_data.province,
                municipality_city=merchant_data.municipality_city,
                barangay=merchant_data.barangay,
                street=merchant_data.street
            )
            db.add(merchant_details)


            # create merchant referral record
            merchant_referral = MerchantReferral(
                referred_by = referral_id,
                referred_merchant = merchant_id
            )
            db.add(merchant_referral)

            
            # Commit changes
            await db.commit()
            await db.refresh(new_merchant)

            logger.info("Merchant created successfully with ID: %s", merchant_id)

            return {
                "status_code": 200,
                "message": "Merchant created successfully.",
                "data": {
                    "merchant_id": merchant_id,
                    "mobile_number": merchant_data.mobile_number,
                    "business_name": merchant_data.business_name,
                    "business_type": merchant_data.business_type
                }
            }

        except IntegrityError as e:
            await db.rollback()
            logger.error("IntegrityError while creating merchant: %s", str(e))
            return {
                "status_code": 400,
                "message": "Database integrity error. Possibly duplicate data.",
                "data": None
            }

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error("SQLAlchemyError while creating merchant: %s", str(e))
            return {
                "status_code": 500,
                "message": "Internal server error while creating merchant.",
                "data": None
            }

        except Exception as e:
            await db.rollback()
            logger.critical("Unexpected error while creating merchant: %s", str(e), exc_info=True)
            return {
                "status_code": 500,
                "message": "An unexpected error occurred.",
                "data": None
            }
        

    @staticmethod
    async def get_merchant_by_id(db: AsyncSession, merchant_id: str):
        try:
            # Fetch merchant with details
            stmt = select(Merchant).where(
                Merchant.merchant_id == merchant_id
            ).options(joinedload(Merchant.details))
            
            result = await db.execute(stmt)
            merchant = result.scalars().first()

            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found.")

            # Fetch the associated member using mobile_number
            member_stmt = select(Member).where(
                Member.mobile_number == merchant.mobile_number
            ).options(joinedload(Member.details))

            member_result = await db.execute(member_stmt)
            member = member_result.scalars().first()

            # Get member details if available
            member_details = member.details if member and member.details else None

            return {
                "merchant_id": merchant.merchant_id,
                "business_name": merchant.business_name,
                "business_type": merchant.business_type,
                "discount": merchant.discount,
                "merchant_wallet": merchant.merchant_wallet,
                "reward_points": merchant.reward_points,
                "created_at": merchant.created_at,
                "updated_at": merchant.updated_at,
                "details": {
                    "latitude": merchant.details.latitude,
                    "longitude": merchant.details.longitude,
                    "region": merchant.details.region,
                    "province": merchant.details.province,
                    "municipality_city": merchant.details.municipality_city,
                    "barangay": merchant.details.barangay,
                    "street": merchant.details.street,
                } if merchant.details else None,
                "member": {
                    "member_id": member.member_id if member else None,
                    "full_name": f"{member_details.first_name} {member_details.middle_name or ''} {member_details.last_name} {member_details.suffix_name or ''}".strip()
                } if member_details else None
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving merchant: {str(e)}")


    @staticmethod
    async def get_merchant_by_id2(db: AsyncSession, merchant_id: str):
        try:
            stmt = select(Merchant).where(
                Merchant.merchant_id == merchant_id).options(joinedload(Merchant.details))
            result = await db.execute(stmt)

            merchant = result.scalars().first()

            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found.")

            return {
                "merchant_id": merchant.merchant_id,
                "mobile_number": merchant.mobile_number,
                "business_name": merchant.business_name,
                "business_type": merchant.business_type,
                "discount": merchant.discount,
                "merchant_wallet": merchant.merchant_wallet,
                "reward_points": merchant.reward_points,
                "created_at": merchant.created_at,
                "updated_at": merchant.updated_at,
                "details": {
                    "latitude": merchant.details.latitude,
                    "longitude": merchant.details.longitude,
                    "region": merchant.details.region,
                    "province": merchant.details.province,
                    "municipality_city": merchant.details.municipality_city,
                    "barangay": merchant.details.barangay,
                    "street": merchant.details.street,
                } if merchant.details else None
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving merchant: {str(e)}")



    @staticmethod
    async def get_all_merchants(db: AsyncSession):
        result = await db.execute(
            select(Merchant)
            .options(
                selectinload(Merchant.details),  # Eager load MerchantDetails
                selectinload(Merchant.member).selectinload(Member.details)  # Load the Member and its details
            )
        )
        merchants = result.scalars().all()
        
        return [
            {
                "merchant_id": m.merchant_id,
                "mobile_number": m.mobile_number,
                "business_name": m.business_name,
                "business_type": m.business_type,
                "discount": m.discount,
                "merchant_wallet": m.merchant_wallet,
                "reward_points": m.reward_points,
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
                "updated_at": m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
                "manager": " ".join(filter(None, [
                    m.member.details.first_name if m.member and m.member.details else None,
                    m.member.details.middle_name if m.member and m.member.details and m.member.details.middle_name else None,
                    m.member.details.last_name if m.member and m.member.details else None,
                    m.member.details.suffix_name if m.member and m.member.details and m.member.details.suffix_name else None
                ])).strip() if m.member and m.member.details else None,
                "details": {
                    "latitude": m.details.latitude,
                    "longitude": m.details.longitude,
                    "region": m.details.region,
                    "province": m.details.province,
                    "municipality_city": m.details.municipality_city,
                    "barangay": m.details.barangay,
                    "street": m.details.street
                } if m.details else None
            }
            for m in merchants
        ]


    @staticmethod
    async def get_merchant_purchase_history(db: AsyncSession, merchant_id: str):

        try:
            merchant = await MerchantRepo.get_merchant_by_id(db, merchant_id)

            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")
            
            query = (
                select(
                    MerchantPurchaseHistory.purchase_id,
                    MerchantPurchaseHistory.merchant_id,
                    MerchantPurchaseHistory.amount,
                    MerchantPurchaseHistory.reference_id,
                    MerchantPurchaseHistory.status,
                    MerchantPurchaseHistory.created_at.label("purchase_date"),
                    MemberDetails.first_name,
                    MemberDetails.middle_name,
                    MemberDetails.last_name,
                    MemberDetails.suffix_name,
                )
                .join(Member, MerchantPurchaseHistory.member_id == Member.member_id)
                .join(MemberDetails, Member.member_id == MemberDetails.member_id)
                .filter(MerchantPurchaseHistory.merchant_id == merchant_id)
            )

            result = await db.execute(query)
            purchases = result.fetchall()
            
            print("qwe", str(query))
            if not purchases:
                return [] # this is where the error is

            purchase_list = []
            for purchase in purchases:
                name = " ".join(filter(None, [purchase.first_name, purchase.middle_name, purchase.last_name, purchase.suffix_name]))
                purchase_data = {
                    "purchase_id": purchase.purchase_id,
                    "merchant_id": purchase.merchant_id,
                    "name": name,
                    "amount": purchase.amount,
                    "reference_id": purchase.reference_id,
                    "status": purchase.status,
                    "purchase_date": purchase.purchase_date.isoformat(),
                }
                purchase_list.append(purchase_data)

            return purchase_list
        
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving merchant purchase history: {str(e)}")

        

