from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.repo.investor_repo import InvestorRepo
from api.v1.schemas.investor_schemas import InvestorDashboardResponse

class InvestorService:
    @staticmethod
    async def get_dashboard_data(db: AsyncSession, member_id: str) -> InvestorDashboardResponse:
        return await InvestorRepo.get_dashboard_data(db, member_id)
    
    @staticmethod
    async def get_monthly_activation_data(db: AsyncSession) -> list:
        return await InvestorRepo.get_monthly_activation_data(db)
