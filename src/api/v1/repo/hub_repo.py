from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from sqlalchemy.future import select
from sqlalchemy import func, or_

from models.hub_models import Hub

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from uuid import uuid4 

from api.v1.schemas.hub_schemas import CreateHub, HubListResponse
from api.v1.repo.member_repo import MemberRepo

from models.member_models import Member, MemberDetails

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

class HubRepo:
    @staticmethod
    async def create_hub(db: AsyncSession, hub_data: CreateHub):
        try:
            
            logger.debug("Starting Hub creation process")

            result = await db.execute(
                select(Hub).where(
                    or_(
                        Hub.hub_name == hub_data.hub_name,
                        Hub.hub_user == hub_data.hub_user
                    )
                )
            )

            existing_hub = result.scalars().first()

            if existing_hub:
                if existing_hub.hub_name == hub_data.hub_name:
                    logger.warning("Hub already existed!")
                    raise HTTPException(status_code=400, detail="Hub already exists.")
                elif existing_hub.hub_user == hub_data.hub_user:
                    logger.warning("Hub User already assigned to another hub!")
                    raise HTTPException(status_code=400, detail="Hub User already assigned to another hub.")
                
            try:
                member = await MemberRepo.get_member_by_mobile_number(db, hub_data.hub_user)
            except HTTPException as e:
                raise e
            
            new_hub = Hub(
                hub_name = hub_data.hub_name,
                hub_user = hub_data.hub_user,
                region = hub_data.region,
                province = hub_data.province,
                municipality_city = hub_data.municipality_city
            )

            db.add(new_hub)
            await db.commit()
            await db.refresh(new_hub)

            logger.debug("New hub added: %s", new_hub.id)

            return new_hub

        except Exception as e:
            logger.error(f"Error creating hub: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def get_all_hubs(session: AsyncSession):
        query = (
            select(Hub, Member, MemberDetails)
            .join(Member, Hub.hub_user == Member.mobile_number)
            .outerjoin(MemberDetails, Member.member_id == MemberDetails.member_id)
            .options(joinedload(Hub.owner).joinedload(Member.details))
        )
        
        result = await session.execute(query)
        hubs = result.all()
        
        hub_list = []
        for hub, member, details in hubs:
            full_name = format_name(details)
            
            hub_list.append(HubListResponse(
                id=hub.id,
                reward_points=hub.reward_points,
                hub_name=hub.hub_name,
                hub_user=member.mobile_number,  # Keeping mobile_number for reference
                hub_user_id=member.member_id,  # Added to return member_id
                region=hub.region,
                province=hub.province,
                municipality_city=hub.municipality_city,
                barangay=hub.barangay if hub.barangay else "",
                hub_user_name=full_name,  # Include formatted name
                created_at=hub.created_at.isoformat()
            ))
        
        return hub_list