from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    Float
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4



from core.database import Base


class Community(Base):
    __tablename__ = "communities"

    community_id = Column(String(36), index=True,  primary_key=True, default=lambda: str(uuid4()))
    community_name = Column(String(155), nullable=False, unique=True)
    community_leader = Column(String(10), nullable=True)
    reward_points = Column(Float, nullable=False, default=0.00)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    members = relationship("Member", back_populates="community")
