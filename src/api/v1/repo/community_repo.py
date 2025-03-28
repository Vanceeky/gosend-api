from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, aliased, outerjoin
from sqlalchemy.future import select
from sqlalchemy import func
from models.community_models import Community


from models.member_models import Member, MemberDetails, MemberAddress

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


from api.v1.schemas.community_schemas import CreateCommunity
from api.v1.repo.member_repo import MemberRepo

from uuid import uuid4
from sqlalchemy import or_
import traceback
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class CommunityRepo:
    @staticmethod
    async def create_community(db: AsyncSession, community_data: CreateCommunity):
        try:
            logger.debug("Starting community creation process")

            # Combine the first two queries using OR condition
            result = await db.execute(
                select(Community).where(
                    or_(
                        Community.community_name == community_data.community_name,
                        Community.community_leader == community_data.community_leader
                    )
                )
            )

            existing_community = result.scalars().first()

            if existing_community:
                if existing_community.community_name == community_data.community_name:
                    logger.warning("Community already existed!")
                    raise HTTPException(status_code=400, detail="Community already exists.")
                elif existing_community.community_leader == community_data.community_leader:
                    logger.warning("Community Leader already assigned to another community!")
                    raise HTTPException(status_code=400, detail="Community Leader already assigned to another community.")

            # Validate if the community_leader exists
            try:
                member = await MemberRepo.get_member_by_mobile_number(db, community_data.community_leader)
            except HTTPException as e:
                raise e

            # Create new community
            new_community = Community(
                community_id=str(uuid4()),
                community_name=community_data.community_name,
                community_leader=community_data.community_leader
            )

            logger.debug("New Community created with ID: %s", new_community.community_id)

            member.account_type = "LEADER"
            db.add(member)
            
            db.add(new_community)
            await db.commit()
            await db.refresh(new_community)

            return new_community

        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=str(e))




    @staticmethod
    async def get_all_communities2(db: AsyncSession):
        # Query to fetch communities with leader details and total members
        query = (
            select(
                Community.community_id,
                Community.community_name,
                MemberDetails.first_name.label("leader_name"),
                func.count(Member.member_id).label("total_members"),
                Community.reward_points,
                Community.created_at.label("date_added")
            )
            .outerjoin(Member, Community.community_id == Member.community_id)
            .outerjoin(MemberDetails, Member.member_id == MemberDetails.member_id)
            .filter(Member.account_type == "LEADER")
            .group_by(
                Community.community_id,
                MemberDetails.first_name
            )
        )

        result = await db.execute(query)
        communities = result.all()
        return communities
            
    @staticmethod
    async def get_all_communities(db: AsyncSession):
        # Subquery to fetch the leader's details using the mobile_number
        leader_subquery = (
            select(
                Member.mobile_number,
                func.concat_ws(
                    " ",  # Separator (space)
                    MemberDetails.first_name,
                    MemberDetails.middle_name,
                    MemberDetails.last_name,
                    MemberDetails.suffix_name
                ).label("leader_full_name")
            )
            .join(MemberDetails, Member.member_id == MemberDetails.member_id)
            .subquery()
        )

        # Subquery to count total members in each community
        members_count_subquery = (
            select(
                Member.community_id,
                func.count(Member.member_id).label("total_members")
            )
            .group_by(Member.community_id)
            .subquery()
        )

        # Main query to fetch communities with leader and total members
        query = (
            select(
                Community.community_id,
                Community.community_name,
                func.coalesce(leader_subquery.c.leader_full_name, "N/A").label("leader_name"),
                func.coalesce(members_count_subquery.c.total_members, 0).label("total_members"),
                Community.reward_points,
                Community.created_at.label("date_added")
            )
            .outerjoin(leader_subquery, Community.community_leader == leader_subquery.c.mobile_number)
            .outerjoin(members_count_subquery, Community.community_id == members_count_subquery.c.community_id)
        )

        result = await db.execute(query)
        communities = result.all()
        return communities



    @staticmethod
    async def get_community(db: AsyncSession, community_id: str):
        # Fetch the community
        community_query = select(Community).where(Community.community_id == community_id)
        community_result = await db.execute(community_query)
        community = community_result.scalar()

        if not community:
            return None

        # Fetch the leader details
        leader_query = (
            select(
                Member.member_id.label("user_id"),
                Member.mobile_number,
                Member.account_type,
                MemberDetails.first_name,
                MemberDetails.middle_name,
                MemberDetails.last_name,
                MemberDetails.suffix_name,
                Member.is_activated,
                Member.is_kyc_verified
            )
            .join(MemberDetails, Member.member_id == MemberDetails.member_id)
            .where(Member.mobile_number == community.community_leader)
        )
        leader_result = await db.execute(leader_query)
        leader = leader_result.first()

        # Fetch all members of the community
        members_query = (
            select(
                Member.member_id.label("user_id"),
                Member.mobile_number,
                Member.account_type,
                MemberDetails.first_name,
                MemberDetails.middle_name,
                MemberDetails.last_name,
                MemberDetails.suffix_name,
                Member.is_activated,
                Member.is_kyc_verified
            )
            .join(MemberDetails, Member.member_id == MemberDetails.member_id)
            .where(Member.community_id == community_id)
        )
        members_result = await db.execute(members_query)
        members = members_result.all()

        return {
            "community_name": community.community_name,
            "reward_points": community.reward_points,
            "leader": leader,
            "members": members
        }

