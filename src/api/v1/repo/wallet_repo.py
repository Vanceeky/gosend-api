from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from models.wallet_models import Wallet, WalletExtensions



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