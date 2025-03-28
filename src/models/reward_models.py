from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    TIMESTAMP,
    Float,
    Enum
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from uuid import uuid4

from core.database import Base

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    reward_source_type = Column(String(120), nullable=False)
    reward_points = Column(Float, nullable=False)

    reward_from = Column(String(36), ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    receiver = Column(String(36), ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)


    title = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)

    status = Column(String(50), nullable=False)

    reference_id = Column(String(36), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


    # Relationships
    giver = relationship("Member", foreign_keys=[reward_from], back_populates="rewards_given")
    recipient = relationship("Member", foreign_keys=[receiver], back_populates="rewards_received")

