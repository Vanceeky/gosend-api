from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import uuid4

from api.v1.schemas.member_schemas import MemberCreateSchema, MemberReadSchema

from api.v1.repo.member_repo import MemberRepo

class MemberService:
    @staticmethod
    async def create_member(db: AsyncSession, member_data: MemberCreateSchema, ):
        """Create a new member along with details, address, and wallet."""
        try:
            # Step 1: Create the Member
            new_member = await MemberRepo.create_member(db, member_data)

            return new_member

        except IntegrityError:
            await db.rollback()
            raise ValueError("Member already exists or invalid data.")
        
        except Exception as e:
            raise e
