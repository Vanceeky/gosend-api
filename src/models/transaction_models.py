from sqlalchemy import (
    Column,
    String, 
    TIMESTAMP,
    Enum,
    DECIMAL,
    TEXT,
    ForeignKey,
    Float

)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from uuid import uuid4

from core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    sender_id = Column(String(36), nullable=False)
    receiver_id = Column(String(36), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(50), nullable=False)

    transaction_type = Column(Enum('CASH-IN', 'CASH-OUT'), nullable=False)

    status = Column(Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, server_default='pending', default='pending')

    # TOPWALLET reference ID
    reference_id = Column(String(120), nullable=False)
    extra_metadata = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

