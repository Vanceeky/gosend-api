from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.services.reward_services import RewardService

from core.database import get_db


router = APIRouter()




@router.get("/", summary="Get all rewards")
async def get_rewards(db: AsyncSession = Depends(get_db)):
    return await RewardService.fetch_all_rewards(db)
    