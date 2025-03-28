from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from api.v1.schemas.merchant_schemas import MerchantResponse, MerchantCreate, MerchantPurchaseHistoryListResponse
from api.v1.services.merchant_services import MerchantService
from fastapi import HTTPException
from core.security import JWTBearer, decode_jwt, require_role, get_jwt_identity

from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("s/", summary="Get all merchants with details", dependencies=[Depends(require_role("ADMIN", "MERCHANT", "INVESTOR", "CUSTOMER_SUPPORT"))])
async def get_all_merchants(db: AsyncSession = Depends(get_db)):
    return await MerchantService.get_all_merchants(db)


@router.post("/create/{referral_id}", response_model=MerchantResponse, summary="Register a new merchant")
async def create_merchant(referral_id: str, merchant_data: MerchantCreate, db: AsyncSession = Depends(get_db)):
    return await MerchantService.create_merchant(db, merchant_data, referral_id)


#, dependencies=[Depends(require_role("ADMIN", "MERCHANT"))]
@router.get("/{merchant_id}", summary="Get merchant details", dependencies=[Depends(require_role("ADMIN", "MERCHANT", "INVESTOR", "CUSTOMER_SUPPORT"))])
async def get_merchant(
    merchant_id: str = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    # Decode the token to get merchant_id
    token_merchant_id = token['user_id']

    # If the requester is a merchant, they can only view their own details
    if token_merchant_id and not merchant_id:
        merchant_id = token_merchant_id
    elif not token_merchant_id and not merchant_id:
        raise HTTPException(status_code=400, detail="Merchant ID is required.")

    return await MerchantService.get_merchant(db, merchant_id)

# For logged-in merchants using the token
@router.get("/", summary="Get own merchant details", dependencies=[Depends(require_role("MERCHANT"))])
async def get_own_merchant(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    
    merchant_id = token['user_id']
    return await MerchantService.get_merchant(db, merchant_id)




@router.get("/purchase/history", response_model=List[MerchantPurchaseHistoryListResponse],dependencies=[Depends(require_role("MERCHANT"))])
async def get_merchant_purchase_history(
    db: AsyncSession = Depends(get_db),
    token_payload: dict = Depends(JWTBearer()),
):
    merchant_id = token_payload['user_id']
    return await MerchantService.get_merchant_purchase_history(db, merchant_id)





