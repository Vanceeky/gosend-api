from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.services.TopWallet import TopWallet
from api.v1.repo.member_repo import MemberRepo
from api.v1.schemas.topwallet_schemas import P2PprocessRequest, P2PTransferRequest, TWP2PTransferRequest

from core.database import get_db
from core.security import JWTBearer, require_role


router = APIRouter()



@router.post("/get-banks-list")
async def get_banks_list():
    return await TopWallet.get_banks_list()
    

@router.post("/cashin_by_bank_id", dependencies=[Depends(require_role("MEMBER"))])
async def cashin_by_bank_id(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(JWTBearer())
):
    member_id = token.get("user_id")
    member_id = await MemberRepo.get_external_id(db, member_id)
    return await TopWallet.cashin_bank_by_id(member_id)

@router.post("/get_profile", dependencies=[Depends(require_role("MEMBER"))])
async def get_profile(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(JWTBearer())
):
    member_id = token.get("user_id")

    member_id = await MemberRepo.get_external_id(db, member_id)
    return await TopWallet.get_profile(member_id)

@router.post("/generate/qrph", dependencies=[Depends(require_role("MEMBER"))])
async def generate_qr(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(JWTBearer())
):
    member_id = token.get("user_id")

    member_id = await MemberRepo.get_external_id(db, member_id)
    return await TopWallet.generate_qr(member_id)


@router.post("/initiate_p2ptransfer", dependencies=[Depends(require_role("MEMBER"))])
async def initiate_p2ptransfer(
    data: TWP2PTransferRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(JWTBearer())
):
    member_id = token.get("user_id")
    return await TopWallet.p2p_transfer(db, data, member_id)


@router.post("process_p2ptransfer", dependencies=[Depends(require_role("MEMBER"))])
async def process_p2ptransfer(
    data: P2PprocessRequest,
):
    return await TopWallet.process_transfer_p2p(data)