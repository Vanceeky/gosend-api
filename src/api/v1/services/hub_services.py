from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from utils.responses import json_response
from fastapi import HTTPException

from api.v1.repo.hub_repo import HubRepo
from api.v1.schemas.hub_schemas import CreateHub

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class HubService:
    @staticmethod
    async def create_hub(db: AsyncSession, hub_data: CreateHub):
        try:

            result = await HubRepo.create_hub(db, hub_data)

            if result:
                return json_response(
                    message = "Hub Created Successfully!",
                    status_code = 200
                )
            
        except Exception as e:
            raise e
        
    @staticmethod
    async def get_all_hubs(db: AsyncSession):
        return await HubRepo.get_all_hubs(db)

        