from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    TIMESTAMP
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from core.database import Base

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    referred_by = Column(String(36), ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)
    referred_member = Column(String(36), ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)


    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


    # Relationships (Fixed)
    referrer = relationship("Member", foreign_keys=[referred_by], back_populates="referrals_made")
    referred = relationship("Member", foreign_keys=[referred_member], back_populates="referred_by_member")
