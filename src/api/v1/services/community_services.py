from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from utils.responses import json_response

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from api.v1.repo.community_repo import CommunityRepo
from api.v1.schemas.community_schemas import CreateCommunity, CommunityResponse, CommunityListResponse, LeaderResponse, MemberResponse

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class CommunityService:
    @staticmethod
    async def create_community(db: AsyncSession, community_data: CreateCommunity) -> CommunityResponse:
        
        result = await CommunityRepo.create_community(db, community_data)

        if result:
            return json_response(
                message = "Community created successfully!",
                status_code=200
            )
        

    @staticmethod
    async def get_all_communities2(db: AsyncSession) -> JSONResponse:
        # Fetch data from the repository
        communities = await CommunityRepo.get_all_communities(db)

        # Format the data into the CommunityListResponse schema
        formatted_communities = [
            CommunityListResponse(
                community_id=community.community_id,
                community_name=community.community_name,
                leader_name=community.leader_name,
                total_members=community.total_members,
                reward_points=community.reward_points,
               # date_added=community.date_added.strftime("%Y-%m-%d %H:%M:%S"), # Convert datetime to string
            ).model_dump()  # Convert Pydantic model to dictionary
            for community in communities
        ]

        # Return the JSON response using your utility
        return json_response(
            message="Communities fetched successfully",
            status_code=200,
            data=formatted_communities
        )
    @staticmethod
    async def get_all_communities(db: AsyncSession) -> JSONResponse:
        # Fetch data from the repository
        communities = await CommunityRepo.get_all_communities(db)

        # Format the data into the CommunityListResponse schema
        formatted_communities = [
            CommunityListResponse(
                community_id=community.community_id,
                community_name=community.community_name,
                leader_name=community.leader_name if community.leader_name else "N/A",
                total_members=community.total_members,
                reward_points=community.reward_points,
            ).model_dump()  # Convert Pydantic model to dictionary
            for community in communities
        ]

        # Return the JSON response using your utility
        return json_response(
            message="Communities fetched successfully",
            status_code=200,
            data=formatted_communities
        )

    @staticmethod
    async def get_community(db: AsyncSession, community_id: str):
        # Fetch data from the repository
        community_data = await CommunityRepo.get_community(db, community_id)

        if not community_data:
            raise HTTPException(status_code=404, detail="Community not found")

        # Convert Row to dictionary for the leader
        leader_dict = dict(community_data["leader"]._asdict()) if community_data["leader"] else None

        # Format the leader
        leader = LeaderResponse(**leader_dict) if leader_dict else None

        # Convert Rows to dictionaries for the members
        members = [MemberResponse(**dict(member._asdict())) for member in community_data["members"]]

        # Build the response data
        response_data = {
            "community_name": community_data["community_name"],
            "reward_points": community_data["reward_points"],  # Add reward_points
            "leader": leader.dict() if leader else None,
            "members": [member.dict() for member in members]
        }

        # Return the JSON response using your utility
        return json_response(
            message="Community members retrieved successfully",
            status_code=200,
            data=response_data
        )