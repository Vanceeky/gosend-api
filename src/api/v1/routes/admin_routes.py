from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from api.v1.schemas.admin_schemas import AdminAccountCreate, AdminAccountResponse, AdminLoginRequest, ProcessActivation
from api.v1.services.admin_services import AdminService
from fastapi import status
from typing import List

from core.security import JWTBearer, require_role
from utils.responses import json_response


from fastapi import Response


router = APIRouter()



@router.post("/create", response_model=AdminAccountResponse)
async def create_account(
    account_data: AdminAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    return await AdminService.create_account(db, account_data)

@router.post('/{account_url}/login', status_code=status.HTTP_200_OK)
async def login_account(account_url: str, login_data: AdminLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await AdminService.login_account(db, account_url, login_data, response)
    
    return {
        "message": result.get("message"),
        "data": result.get("data"),
        "status_code": result.get("status_code")
    }






@router.get("/all", response_model=List[AdminAccountResponse])
async def get_all_accounts(db: AsyncSession = Depends(get_db)):
    return await AdminService.get_all_accounts(db)

@router.post("/initiate-member-activation", status_code=status.HTTP_200_OK, dependencies=[Depends(require_role("ADMIN", "CUSTOMER_SUPPORT", "LEADER"))])
async def initiate_member_activation(db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    activated_by = token['member_user_id']
    print("activated_by_external_id", activated_by)
    return await AdminService.initiate_member_activation(db, activated_by)

@router.post("/process-member-activation", status_code=status.HTTP_200_OK, dependencies=[Depends(require_role("ADMIN", "CUSTOMER_SUPPORT", "LEADER"))])
async def process_member_activation(
    activation_data: ProcessActivation,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    activated_by = token['member_user_id']
    print("qwerty", activation_data)
    return await AdminService.process_member_activation(db, activation_data, activated_by)

