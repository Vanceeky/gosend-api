from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.activation_schema import ActivationHistorySchema
from api.v1.repo.activation_repo import ActivationRepo

class ActivationService:
    @staticmethod
    async def get_activation_history_with_member_name(db: AsyncSession) -> List[ActivationHistorySchema]:
        activations = await ActivationRepo.get_activation_history(db)
        
        activation_history_list = []
        
        for activation in activations:
            # Safely get the member name (handle cases where details might be None)
            member_name = ""
            if activation.member and activation.member.details:
                member_name = f"{activation.member.details.first_name} {activation.member.details.last_name}"

            activation_history_data = ActivationHistorySchema(
                activation_id=activation.id,
                activated_member_name=member_name,
                activated_at=activation.created_at,
                amount=activation.amount,
                currency=activation.currency,
                status=activation.status,
                reference_id=activation.reference_id,
                extra_metadata=activation.extra_metadata,
                # You might want to add these fields too:
                member_id=activation.member_id,
                activated_by=activation.activated_by,
                activated_by_role=activation.activated_by_role,
                created_at = activation.created_at.isoformat()
            )
            
            activation_history_list.append(activation_history_data)
        
        return activation_history_list

