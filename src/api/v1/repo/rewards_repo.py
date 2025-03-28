from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import text



from models.reward_models import Reward
from models.member_models import MemberDetails, Member

from api.v1.repo.member_repo import MemberRepo
from api.v1.schemas.reward_schemas import RewardSchema, RewardListSchema
from fastapi import HTTPException
from utils.extra import format_name

import traceback
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class RewardRepo:
    
    @staticmethod
    async def get_member_rewards(db: AsyncSession, member_id: str):
        try:
            # Query rewards with related giver and recipient details
            stmt = (
                select(Reward)
                .options(
                    joinedload(Reward.giver).joinedload(Member.details),  # ✅ Use class attributes
                    joinedload(Reward.recipient).joinedload(Member.details)  # ✅ Use class attributes
                )
                .where(Reward.receiver == member_id)
            )

            result = await db.execute(stmt)
            rewards = result.scalars().all()

            reward_list = []
            total_rewards = 0

            for reward in rewards:
                giver_details = reward.giver.details if reward.giver else None
                recipient_details = reward.recipient.details if reward.recipient else None

                reward_list.append({
                    "id": reward.id,
                    "reward_source_type": reward.reward_source_type,
                    "reward_points": reward.reward_points,
                    "reward_from": reward.reward_from,
                    "reward_from_name": format_name(giver_details),
                    "receiver": reward.receiver,
                    "receiver_name": format_name(recipient_details),
                    "title": reward.title,
                    "description": reward.description,
                    "status": reward.status,
                    "reference_id": reward.reference_id,
                    "created_at": reward.created_at,
                    "updated_at": reward.updated_at,
                })

                total_rewards += reward.reward_points

            return {
                "receiver": member_id,
                "total_rewards": total_rewards,
                "rewards": reward_list
            }

        except Exception as e:
            logger.error("Error occurred getting member rewards: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


    @staticmethod
    async def get_all_rewards(db: AsyncSession):
        try:

            stmt = await db.execute(
                select(Reward)
            )

        except Exception as e:
            raise e

    @staticmethod   
    async def get_all_rewards(db: AsyncSession):
        query = (
            select(Reward)
            .options(
                joinedload(Reward.giver).joinedload(Member.details),  # ✅ Load giver's details properly
                joinedload(Reward.recipient).joinedload(Member.details)  # ✅ Load recipient's details properly
            )
        )
        
        result = await db.execute(query)
        rewards = result.scalars().all()
        
        return [
            {
                "id": reward.id,
                "title": reward.title,
                "reward_source_type": reward.reward_source_type,
                "description": reward.description,
                "reward_points": reward.reward_points,
                "status": reward.status,
                "reference_id": reward.reference_id,
                "created_at": reward.created_at,
                "updated_at": reward.updated_at,
                "reward_from": {
                    "member_id": reward.reward_from,
                    "full_name": f"{reward.giver.details.first_name} {reward.giver.details.middle_name or ''} {reward.giver.details.last_name} {reward.giver.details.suffix_name or ''}".strip()
                    if reward.giver and reward.giver.details else None
                },
                "receiver": {
                    "member_id": reward.receiver,
                    "full_name": f"{reward.recipient.details.first_name} {reward.recipient.details.middle_name or ''} {reward.recipient.details.last_name} {reward.recipient.details.suffix_name or ''}".strip()
                    if reward.recipient and reward.recipient.details else None
                }
            }
            for reward in rewards
        ]





