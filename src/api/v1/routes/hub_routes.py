from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from api.v1.schemas.hub_schemas import CreateHub, HubListResponse
from api.v1.services.hub_services import HubService
from typing import List

from core.security import require_role, JWTBearer



from core.security import require_role, JWTBearer

router = APIRouter()

@router.post("/create", dependencies=[Depends(require_role("ADMIN"))])
async def create_hub(hub_data: CreateHub, db: AsyncSession = Depends(get_db)):
    return await HubService.create_hub(db, hub_data)

@router.get("/all", response_model=List[HubListResponse], dependencies=[Depends(require_role("ADMIN"))])
async def get_hubs(db: AsyncSession = Depends(get_db)):
    return await HubService.get_all_hubs(db)