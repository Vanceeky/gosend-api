from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    TIMESTAMP,
    Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from uuid import uuid4

from core.database import Base


class Investor(Base):
    __tablename__ = "investors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # One-to-One Relationship with Member
    investor = Column(String(36), ForeignKey("members.mobile_number", ondelete="CASCADE"), nullable=False, unique=True)

    reward_points = Column(Float, nullable=False, default=0)
    address = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship to Member
    owner = relationship("Member", back_populates="investor")

