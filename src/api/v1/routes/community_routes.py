from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.v1.schemas.community_schemas import CreateCommunity, CommunityResponse, CommunityListResponse, CommunityDetailsResponse
from api.v1.services.community_services import CommunityService
from core.security import require_role, JWTBearer


from typing import List

router = APIRouter()


# dependencies=[Depends(require_role("ADMIN"))]
@router.post("/create", response_model=CommunityResponse, dependencies=[Depends(require_role("ADMIN"))] )
async def create_community(
    community_data: CreateCommunity,
    db: AsyncSession = Depends(get_db)
):
    return await CommunityService.create_community(db, community_data)


@router.get("/all", response_model=List[CommunityListResponse], dependencies=[Depends(require_role("ADMIN", "INVESTOR", "CUSTOMER_SUPPORT"))])
async def get_all_communities_endpoint(db: AsyncSession = Depends(get_db)):
    return await CommunityService.get_all_communities(db)


@router.get("/{community_id}", response_model=CommunityDetailsResponse, dependencies=[Depends(require_role("ADMIN", "INVESTOR", "CUSTOMER_SUPPORT"))])
async def get_community(community_id: str, db: AsyncSession = Depends(get_db)):
    return await CommunityService.get_community(db, community_id)


@router.get("/", summary="Get own community details", dependencies=[Depends(require_role("LEADER"))], response_model=CommunityDetailsResponse)
async def get_own_community(db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    return await CommunityService.get_community(db, token['user_id'])