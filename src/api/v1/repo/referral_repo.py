   
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.member_models import Member
from fastapi import HTTPException
import traceback
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed




class ReferralRepo:
    pass