from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from api.v1.schemas.member_schemas import MemberCreateSchema, MemberReadSchema, MemberListResponse, MemberInfoSchema, PurchaseHistorySchema
from api.v1.schemas.reward_schemas import RewardListSchema
from api.v1.services.member_services import MemberService
from api.v1.repo.member_repo import MemberRepo
from api.v1.services.reward_services import RewardService
from core.security import JWTBearer, decode_jwt, require_role, get_jwt_identity


from fastapi.encoders import jsonable_encoder
from typing import List, Optional

from fastapi import HTTPException


router = APIRouter()

@router.post("/create/{referral_id}", response_model=MemberReadSchema)
async def create_member(referral_id: str, member_data: MemberCreateSchema, db: AsyncSession = Depends(get_db)):
    """
    Create a new member, including details, address, and wallet.
    """
    new_member = await MemberService.create_member(db, member_data, referral_id)
    print("new member", new_member)
    return new_member

@router.get("/{member_id}/info", response_model=List[MemberInfoSchema])
async def get_member(db: AsyncSession = Depends(get_db), member_id: str = None):
    return await MemberService.get_member(db, member_id)


@router.get("", response_model=List[MemberInfoSchema], summary="Get member details", dependencies=[Depends(require_role("MEMBER"))])
async def get_member(db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    member_user_id = token['user_id']
    return await MemberService.get_member(db, member_user_id)

@router.get("/all", response_model=List[MemberListResponse])
async def get_all_members(
    db: AsyncSession = Depends(get_db),
    is_activated: Optional[bool] = Query(None)  # Accepts is_activated as a query parameter
):
    return await MemberService.get_all_members(db, is_activated)

@router.get('/{member_id}')
async def get_member_balance(db: AsyncSession = Depends(get_db), member_id: str = None):
    return await MemberService.get_member_by_id(db, member_id)



@router.get('/{member_id}/unilevel')
async def get_member_unilevel(db: AsyncSession = Depends(get_db), member_id: str = None):
    return await MemberRepo.get_member_unilevel(db, member_id)


@router.get('/{member_id}/unilevel-5')
async def get_member_unilevel(db: AsyncSession = Depends(get_db), member_id: str = None):
    return await MemberRepo.get_member_unilevel_5(db, member_id)

@router.get("/rewards/all", response_model=RewardListSchema, summary="Get member rewards", dependencies=[Depends(require_role("MEMBER", "ADMIN", "CUSTOMER_SUPPORT"))])
async def get_member_rewards(db: AsyncSession = Depends(get_db), token: dict = Depends(JWTBearer())):
    try:
        member_id = token.get("user_id")
        if not member_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await RewardService.get_member_rewards(db, member_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/rewards/{member_id}", response_model=RewardListSchema, summary="Get member rewards", dependencies=[Depends(require_role("ADMIN", "MEMBER", "INVESTOR"))])
async def get_member_rewards(member_id: str, db: AsyncSession = Depends(get_db)):
    try:

        return await RewardService.get_member_rewards(db, member_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/merchant-purchase/history", response_model=List[PurchaseHistorySchema], dependencies=[Depends(require_role("MEMBER", "ADMIN", "INVESTOR"))])
async def get_member_purchase_history(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(JWTBearer())
):
    member_id = token.get('user_id')
    purchases = await MemberService.get_member_purchase_history(db, member_id)
    if not purchases:
        raise HTTPException(status_code=404, detail="No purchase history found for this member.")
    return purchases

@router.get("/merchant-purchase/history/{member_id}", response_model=List[PurchaseHistorySchema], dependencies=[Depends(require_role("MEMBER", "ADMIN", "INVESTOR"))])
async def get_member_purchase_history(
    member_id: str,
    db: AsyncSession = Depends(get_db),
):
    purchases = await MemberService.get_member_purchase_history(db, member_id)
    if not purchases:
        raise HTTPException(status_code=404, detail="No purchase history found for this member.")
    return purchases


