from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from models.wallet_models import Wallet, WalletExtensions
from models.member_models import MemberWallet

from sqlalchemy import update


class WalletRepository:
    @staticmethod
    async def get_wallet_extension(db: AsyncSession, extension_name: str):
        try:
            result = await db.execute(
                select(WalletExtensions).where(WalletExtensions.extension_name == extension_name)
    
            )

            return result.scalars().first()
        
        except Exception as e:
            raise e
        
    @staticmethod
    async def update_wallet_points(db: AsyncSession, member_id: int, reward_points: int):
        """
        Updates the reward points of a member's wallet.
        """
        wallet_id_subquery = select(MemberWallet.wallet_id).where(MemberWallet.member_id == member_id).scalar_subquery()
        
        await db.execute(
            update(Wallet)
            .where(Wallet.wallet_id == wallet_id_subquery)
            .values(reward_points=reward_points)
        )