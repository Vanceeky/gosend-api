from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.repo.rewards_repo import RewardRepo
from api.v1.schemas.reward_schemas import RewardListSchema

class RewardService:
    @staticmethod
    async def get_member_rewards(db: AsyncSession, member_id: str):
        rewards_data = await RewardRepo.get_member_rewards(db, member_id)

        if not rewards_data:
            return RewardListSchema(receiver=member_id, total_rewards=0.0, rewards=[])

        return rewards_data  # Already formatted in RewardRepo
    

    @staticmethod
    async def fetch_all_rewards(db: AsyncSession):
        return await RewardRepo.get_all_rewards(db)