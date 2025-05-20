from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models.admin_models import AdminAccount
from api.v1.schemas.admin_schemas import AdminAccountCreate

from api.v1.repo.member_repo import MemberRepo
from core.security import hash_password

from fastapi import HTTPException

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



class AdminRepo:
    @staticmethod
    async def create_account(db: AsyncSession, admin_data: AdminAccountCreate):
        try:
            logger.debug("Starting admin account creation")

            try:
                await MemberRepo.get_member_by_mobile_number(db, admin_data.mobile_number)
            except HTTPException as e:
                logger.warning("Mobile number is not registered: %s", admin_data.mobile_number)
                return {
                    "status_code": 400,
                    "message": "Mobile number is not registered!",
                    "data": None
                }

            stmt = select(AdminAccount).where(AdminAccount.mobile_number == admin_data.mobile_number)
            result = await db.execute(stmt)
            existing_account = result.scalar_one_or_none()

            if existing_account:
                logger.warning("Account with mobile number %s already exists.", admin_data.mobile_number)
                return {
                    "status_code": 400,
                    "message": "Account mobile number already registered.",
                    "data": None
                }

            admin_id = str(uuid4())
            account_url = str(uuid4())
            
            new_admin = AdminAccount(
                id=admin_id,
                mobile_number=admin_data.mobile_number,
                username=admin_data.username,
                password=hash_password(admin_data.password),
                account_type=admin_data.account_type,
                account_url=account_url
            )

            db.add(new_admin)
            await db.commit()
            await db.refresh(new_admin)

            logger.info("Admin created successfully with ID: %s", new_admin.id)

            return {
                "status_code": 200,
                "message": "Admin created successfully.",
                "data": {
                    "id": new_admin.id,
                    "mobile_number": new_admin.mobile_number,
                    "username": new_admin.username,
                    "account_type": new_admin.account_type
                }
            }

        except IntegrityError as e:
            await db.rollback()
            logger.error("IntegrityError while creating admin: %s", str(e))
            return {
                "status_code": 400,
                "message": "Database integrity error. Possibly duplicate data.",
                "data": None
            }

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error("SQLAlchemyError while creating admin: %s", str(e))
            return {
                "status_code": 500,
                "message": "Internal server error while creating admin.",
                 "data": None
            }
        
        except Exception as e:
            logger.error("Error occurred during admin account creation: %s", e, exc_info=True)
            raise HTTPException(detail=str(e), status_code=500)
 



    @staticmethod
    async def get_account_by_url(db: AsyncSession, account_url: str):
        result = await db.execute(
            select(AdminAccount).where(AdminAccount.account_url == account_url)
        )

        admin_account = result.scalar()
        if not admin_account:
            raise HTTPException(status_code=404, detail="Invalid Login URL")

        return admin_account
    

    @staticmethod
    async def get_all_accounts(db: AsyncSession):
        result = await db.execute(select(AdminAccount))
        admin_accounts = result.scalars().all()
        return admin_accounts
    


        