from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.services.reward_services import RewardService

from core.database import get_db
from api.v1.schemas.activation_schema import ActivationHistorySchema
from api.v1.services.activation_services import ActivationService

from typing import List

router = APIRouter()




@router.get("/", summary="Get all rewards")
async def get_rewards(db: AsyncSession = Depends(get_db)):
    return await RewardService.fetch_all_rewards(db)
    

@router.get("/activation-history", response_model=List[ActivationHistorySchema])
async def get_activation_history(db: AsyncSession = Depends(get_db)):
    """
    Get the activation history with the activated member's name.
    """
    activation_history = await ActivationService.get_activation_history_with_member_name(db)
    return activation_history