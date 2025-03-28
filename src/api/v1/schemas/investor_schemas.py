from pydantic import BaseModel
from typing import List, Tuple, Literal

class InvestorDashboardResponse(BaseModel):
    reward_points: float
    total_members: int
    activated_members: int
    not_activated_members: int
    total_merchants: int
    total_communities: int
    activations: List[Tuple[Literal['LEADER', 'CUSTOMER SUPPORT', 'MEMBER'], int, int]]  # (activated_by_role, amount, count)
    total_distributed_rewards: float
    total_activator_earnings: float
    total_accumulated_activation_amount: float
    monthly_accumulated_activation: List[Tuple[int, float]]  # (month, total accumulated activation amount)
