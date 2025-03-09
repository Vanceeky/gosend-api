from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from api.v1.schemas.member_schemas import MemberCreateSchema, MemberReadSchema
from api.v1.services.member_services import MemberService

router = APIRouter()

@router.post("/", response_model=MemberReadSchema)
async def create_member(member_data: MemberCreateSchema, db: AsyncSession = Depends(get_db)):
    """
    Create a new member, including details, address, and wallet.
    """
    new_member = await MemberService.create_member(db, member_data)
    print("new member", new_member)
    return new_member