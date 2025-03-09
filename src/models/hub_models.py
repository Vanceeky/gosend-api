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



class Hub(Base):
    __tablename__ = "hubs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    hub_name = Column(String(155), nullable=False)

    hub_user = Column(String(36), ForeignKey("members.mobile_number", ondelete="CASCADE"), nullable=False, unique=True)
    reward_points = Column(Float, nullable=False, default=0)

    address = Column(String(255), nullable=True)

    # Relationship: The owner of this Hub (One-to-One)
    owner = relationship("Member", back_populates="hub")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
