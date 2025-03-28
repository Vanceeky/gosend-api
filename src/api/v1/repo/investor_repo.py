
from sqlalchemy.ext.asyncio import AsyncSession
from models.admin_models import AdminAccount
from models.member_models import Member
from models.merchant_models import Merchant
from models.community_models import Community
from api.v1.schemas.investor_schemas import InvestorDashboardResponse
from sqlalchemy.future import select

from sqlalchemy import func, extract
from api.v1.repo.member_repo import MemberRepo

from models.activation_history_models import ActivationHistory

from sqlalchemy.sql import case


class InvestorRepo:
    @staticmethod
    async def get_dashboard_data(db: AsyncSession, member_id: str):
        # Get member details
        member = await MemberRepo.get_member_by_id(db, member_id)
        mobile_number = member.mobile_number

        # Get investor's total reward points
        result = await db.execute(
            select(AdminAccount.reward_points).where(AdminAccount.mobile_number == mobile_number)
        )
        reward_points = sum(result.scalars().all())

        # Get total members
        total_members = await db.scalar(select(func.count(Member.member_id)))

        # Get activated members
        activated_members = await db.scalar(
            select(func.count(Member.member_id)).where(Member.is_activated == True)
        )

        # Get not activated members
        not_activated_members = total_members - activated_members

        # Get total merchants
        total_merchants = await db.scalar(select(func.count(Merchant.merchant_id)))

        # Get total communities
        total_communities = await db.scalar(select(func.count(Community.community_id)))

        # Get total activations by amount and activated_by_role
        activation_data = await db.execute(
            select(
                ActivationHistory.activated_by_role,
                ActivationHistory.amount,
                func.count(ActivationHistory.id)
            )
            .group_by(ActivationHistory.activated_by_role, ActivationHistory.amount)
        )

        activation_counts = activation_data.all()

        # Calculate total distributed rewards
        total_rewards = sum(
            (count * 55) for _, amount, count in activation_counts if amount == 150
        ) + sum(
            (count * 55) for _, amount, count in activation_counts if amount == 175
        )

        # Calculate total earnings for activators (for activations worth ₱175)
        total_activator_earnings = sum(
            (count * 25) for _, amount, count in activation_counts if amount == 175
        )

        # Calculate total accumulated activation amount
        total_accumulated_activation_amount = sum(
            (count * amount) for _, amount, count in activation_counts
        ) - (total_rewards + total_activator_earnings)

        # Fetch monthly accumulated activation amounts
        monthly_activation_data = await db.execute(
            select(
                extract("month", ActivationHistory.created_at).label("month"),
                func.sum(
                    ActivationHistory.amount 
                    - 55  # Base deduction
                    - case((ActivationHistory.amount == 175, 25), else_=0)  # Conditional deduction
                ).label("total_accumulated_amount")
            )
            .group_by("month")
            .order_by("month")
        )

        # Format monthly data for the frontend graph
        monthly_accumulated_activation = [
            (int(row.month), float(row.total_accumulated_amount)) for row in monthly_activation_data
        ]

        return InvestorDashboardResponse(
            reward_points=reward_points,
            total_members=total_members,
            activated_members=activated_members,
            not_activated_members=not_activated_members,
            total_merchants=total_merchants,
            total_communities=total_communities,
            activations=[(role, amount, count) for role, amount, count in activation_counts],
            total_distributed_rewards=total_rewards,
            total_activator_earnings=total_activator_earnings,
            total_accumulated_activation_amount=total_accumulated_activation_amount,
            monthly_accumulated_activation=monthly_accumulated_activation
        )
    


    
    @staticmethod
    async def get_monthly_activation_data(db: AsyncSession):
        result = await db.execute(
            select(
                extract("month", ActivationHistory.created_at).label("month"),
                func.sum(ActivationHistory.amount).label("total")
            ).group_by("month").order_by("month")
        )

        return [{"month": int(row.month), "total": float(row.total)} for row in result]




