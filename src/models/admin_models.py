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


class AdminAccount(Base):
    __tablename__ = "admin_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    username = Column(String(155), nullable=False, unique=True)

    password = Column(String(255), nullable=False)

    mobile_number = Column(String(10), ForeignKey("members.mobile_number", ondelete="CASCADE"), nullable=True, unique=True)

    account_type = Column(Enum('SUPERADMIN', 'ADMIN', 'CUSTOMER_SUPPORT'), nullable=False, default="CUSTOMER_SUPPORT")

    account_url = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship to Member
    member = relationship("Member", back_populates="admin_account")