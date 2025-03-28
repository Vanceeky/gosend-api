from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    Enum,
    ForeignKey,
    Float
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from uuid import uuid4

from core.database import Base

class ActivationHistory(Base):
    __tablename__ = "activation_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    activated_by = Column(String(36), nullable=False)

    member_id = Column(String(36), ForeignKey("members.member_id"), nullable=False, unique=True)
    amount = Column(Float, nullable=False)

    currency = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)


    activated_by_role = Column(Enum('LEADER', 'CUSTOMER SUPPORT', 'MEMBER'), default="CUSTOMER SUPPORT", nullable=True)
    # topwallet reference id 
    reference_id = Column(String(120), nullable=False)
    extra_metadata = Column(String(255), nullable=True)



    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship with Member
    member = relationship("Member", back_populates="activation_history")
