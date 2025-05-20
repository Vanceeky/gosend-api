from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.repo.rewards_repo import RewardRepo
from api.v1.repo.merchant_repo import MerchantRepo
from api.v1.repo.member_repo import MemberRepo

from api.v1.schemas.reward_schemas import RewardListSchema
from decimal import Decimal

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
    

    @staticmethod
    async def distribute_rewards(db: AsyncSession, reward_pool: float, member_id: str, merchant_id: str, investor_id: str, hub_id: str, reference_id: str):
 

            get_merchant_referrer_member_id = await MerchantRepo.get_merchant_referrer_member_id(db, merchant_id)

            get_direct_referrer_member_id_of_merchant = await MerchantRepo.get_direct_referrer_member_id_of_merchant(db, merchant_id)

            member = await MemberRepo.get_member_by_id(db, member_id)

            member_id = member.member_id
            member_community = member.community_id

            unilevel_5 = await MemberRepo.get_member_unilevel_5(db, member_id)

            print("get_direct_referrer_member_id_of_merchant", get_direct_referrer_member_id_of_merchant)
            print("get_merchant_referrer_member_id", get_merchant_referrer_member_id)
            print("member_id", member_id)
            print("member_community", member_community)
            print("Unilevel 5 levels", unilevel_5)

            print(f"Reward Pooool: {reward_pool}")

            distribution = {
                "Hub": Decimal(reward_pool) * Decimal('0.05'), 
                "Community": Decimal(reward_pool) * Decimal('0.05'), 

                # first level of merchant owner
                "Merchant Direct Referrer": Decimal(reward_pool) * Decimal('0.15'), # direct referrer of user ( first level )
                "User": Decimal(reward_pool) * Decimal('0.1'), # personal rebate
                "Referrer of Merchant": Decimal(reward_pool) * Decimal('0.1'), # referrer of the merchant
                "Investor": Decimal(reward_pool) * Decimal('0.05'),
                "Unilevel Referral": {
                    "Level 1": Decimal(reward_pool) * Decimal('0.06') * Decimal('0.8'),
                    "Level 2": Decimal(reward_pool) * Decimal('0.05') * Decimal('0.8'),
                    "Level 3": Decimal(reward_pool) * Decimal('0.04') * Decimal('0.8'),
                    "Level 4": Decimal(reward_pool) * Decimal('0.03') * Decimal('0.8'),
                    "Level 5": Decimal(reward_pool) * Decimal('0.02') * Decimal('0.8'),
                },
                "Unilevel Remainder to MotherWallet": Decimal(reward_pool) * Decimal('0.04'),
                # change admin_amount to reward_pool
                "Admin (Mother Wallet)": Decimal(reward_pool) * Decimal('0.3'),
            }

            print(f"Distribution: {distribution}")