from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from models.member_models import Member, MemberDetails, MemberAddress, MemberWallet, MemberWalletExtension
from models.wallet_models import Wallet

from api.v1.schemas.member_schemas import MemberCreateSchema
from api.v1.schemas.wallet_schemas import WalletSchema

from api.v1.repo.wallet_repo import WalletRepository
from fastapi import HTTPException

from uuid import uuid4
import traceback


class MemberRepo:

    @staticmethod
    async def create_member(db: AsyncSession, member_data: MemberCreateSchema):
        """Creates a new member along with their details, address, and wallet."""
        try:
            


            # Check if mobile number already exists
            existing_member = await db.execute(select(Member).filter_by(mobile_number=member_data.mobile_number))
            if existing_member.scalars().first():
                raise ValueError("Mobile number already exists!")
            
            # Create new Member instance
            new_member = Member(
                member_id=str(uuid4()),
                mobile_number=member_data.mobile_number,
                #mpin=member_data.mpin,
                account_type=member_data.account_type,
                referral_id = str(uuid4())[:12]  # ✅ Correct way

            )

            # Create Member Details
            member_details = MemberDetails(
                member_id=new_member.member_id,
                first_name=member_data.details.first_name,
                last_name=member_data.details.last_name,
                middle_name=member_data.details.middle_name,
                suffix=member_data.details.suffix,
            )

            # Create Member Address
            member_address = MemberAddress(
                member_id=new_member.member_id,
                house_number=member_data.address.house_number,
                street_name=member_data.address.street_name,
                barangay=member_data.address.barangay,
                city=member_data.address.city,
                province=member_data.address.province,
                region=member_data.address.region,
            )

            # Create Wallet
            new_wallet = Wallet(
                wallet_id=str(uuid4()),
                public_address=str(uuid4()),  # Generate unique wallet address
            )

            member_wallet = MemberWallet(
                wallet_id = new_wallet.wallet_id,
                member_id = new_member.member_id,
                is_primary = True
            )

            extension_name = "TopWallet"
            user_wallet_extension = await WalletRepository.get_wallet_extension(db, extension_name)
            extension_id = user_wallet_extension.wallet_extension_id


            member_wallet_extension = MemberWalletExtension(
                member_wallet_extension_id = str(uuid4()),
                extension_id = extension_id,
                wallet_id = new_wallet.wallet_id,
            )



            # Add to session
            db.add(new_member)
            db.add(member_details)
            db.add(member_address)
            db.add(new_wallet)
            db.add(member_wallet)
            db.add(member_wallet_extension)

            # Commit transaction
            await db.commit()
            await db.refresh(new_member)

            return new_member
        
        except Exception as e:
            print("Error occurred:", str(e))
            traceback.print_exc()  # Prints the full error details
            raise HTTPException(detail=str(e), status_code=500)
