from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.v1.schemas.investor_schemas import InvestorDashboardResponse
from api.v1.services.investor_services import InvestorService

from core.security import JWTBearer, require_role


router = APIRouter()


@router.get("/investor-dashboard", response_model=InvestorDashboardResponse)
async def get_investor_dashboard(
    db: AsyncSession = Depends(get_db),
    token = Depends(JWTBearer()),
):
    member_id = token['member_user_id']
    print("member_idq", member_id)
    return await InvestorService.get_dashboard_data(db, member_id)


@router.get("/activation-history")
async def get_activation_history(db: AsyncSession = Depends(get_db)):
    return await InvestorService.get_monthly_activation_data(db)