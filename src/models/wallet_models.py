from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    TIMESTAMP,
    Float,
    Enum,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from uuid import uuid4

from core.database import Base



class Wallet(Base):
    __tablename__ = "wallets"

    wallet_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    public_address = Column(String(255), nullable=False)

    wallet_balance = Column(Float, nullable=False, default=0.00)
    reward_points = Column(Float, nullable=False, default=0.00)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # One-to-One: Each Wallet can have one associated MemberWallet
    member_wallets = relationship("MemberWallet", back_populates="wallet", uselist=False, cascade="all, delete-orphan")


class WalletExtensions(Base):
    __tablename__ = "wallet_extensions"

    wallet_extension_id = Column(String(36), primary_key=True, index=True)
    extension_name = Column(String(155), nullable=False, index=True)
    extension_type = Column(Enum("monetary"), nullable=False, default="monetary")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # One-to-Many: A WalletExtension can be linked to multiple MemberWalletExtensions
    member_wallet_extensions = relationship("MemberWalletExtension", back_populates="wallet_extension", cascade="all, delete-orphan")



