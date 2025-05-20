from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from typing import List
from models.activation_history_models import ActivationHistory
from models.reward_models import Reward
from models.member_models import Member

from sqlalchemy.ext.asyncio import AsyncSession

class ActivationRepo:
    @staticmethod
    async def get_activation_history(db: AsyncSession) -> List[ActivationHistory]:
        # Use joinedload to eagerly load all relationships in one query
        query = (
            select(ActivationHistory)
            .options(
                joinedload(ActivationHistory.member)
                .joinedload(Member.details)
            )
            .order_by(ActivationHistory.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().unique().all()

