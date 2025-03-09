from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Enum,
    Boolean,
    TIMESTAMP
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
#from models.community_models import Community

from core.database import Base




class Member(Base):
    __tablename__ = "members"

    member_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    mobile_number = Column(String(10), nullable=False, unique=True)
    mpin = Column(String(4), nullable=True)
    account_type = Column(Enum("MEMBER", "MERCHANT", "INVESTOR", "LEADER", "HUB", "ADMIN", "SUPERADMIN", "CUSTOMER_SUPPORT"), nullable=False, default="MEMBER")
    referral_id = Column(String(12), unique=True, nullable=False)
    is_activated = Column(Boolean, nullable=False, default=False)
    is_kyc_verified = Column(Boolean, nullable=False, default=False)

    # Community Relationship
    #community_id = Column(String(36), ForeignKey("communities.community_id", ondelete="SET NULL"), nullable=True)


    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


    # Relationships to member details and address
    details = relationship("MemberDetails", back_populates="member", uselist=False, cascade="all, delete-orphan")
    address = relationship("MemberAddress", back_populates="member", uselist=False, cascade="all, delete-orphan")

  # Relationships
   # community = relationship("Community", back_populates="members")
    
    # Relationship to Hub
    hub = relationship("Hub", back_populates="owner", uselist=False, cascade="all, delete-orphan")

    # Relationship to Investor
    investor = relationship("Investor", back_populates="owner", uselist=False, cascade="all, delete-orphan")

    # In Member model
    admin_account = relationship("AdminAccount", back_populates="member", uselist=False, cascade="all, delete-orphan")

    # One-to-One: A member can have one wallet
    wallet = relationship("MemberWallet", back_populates="member", uselist=False, cascade="all, delete-orphan")



class MemberDetails(Base):
    __tablename__ = "member_details"

    id = Column(String(18), primary_key=True, default=lambda: str(uuid4()))
    member_id = Column(String(36), ForeignKey("members.member_id"), nullable=False, unique=True)
    first_name = Column(String(155), nullable=False)
    last_name = Column(String(155), nullable=False)
    middle_name = Column(String(155), nullable=True)
    suffix_name = Column(String(10), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship to Member
    member = relationship("Member", back_populates="details")


class MemberAddress(Base):
    __tablename__ = "member_address"

    id = Column(String(18), primary_key=True, default=lambda: str(uuid4()))
    member_id = Column(String(36), ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False, unique=True)

    house_number = Column(String(20), nullable=True)
    street_name = Column(String(100), nullable=True)
    barangay = Column(String(100), nullable=True)
    city = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship to Member
    member = relationship("Member", back_populates="address")



class MemberWallet(Base):
    __tablename__ = "member_wallets"

    wallet_id = Column(String(36), ForeignKey("wallets.wallet_id", ondelete="CASCADE"), primary_key=True)
    member_id = Column(String(36), ForeignKey("members.member_id", ondelete="CASCADE"), primary_key=True)

    is_primary = Column(Boolean, nullable=False, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # One-to-One: MemberWallet belongs to one Member
    member = relationship("Member", back_populates="wallet", uselist=False)

    # One-to-One: A MemberWallet links to a Wallet
    wallet = relationship("Wallet", back_populates="member_wallets", uselist=False)
    # One-to-Many: A MemberWallet can have multiple WalletExtensions
    extensions = relationship("MemberWalletExtension", back_populates="member_wallet", cascade="all, delete-orphan")



class MemberWalletExtension(Base):
    __tablename__ = "member_wallet_extensions"

    member_wallet_extension_id = Column(String(36), primary_key=True)

    extension_id = Column(String(36), ForeignKey("wallet_extensions.wallet_extension_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)

    wallet_id = Column(String(36), ForeignKey("member_wallets.wallet_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)

    external_id = Column(String(155), nullable=True, index=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Many-to-One: Each MemberWalletExtension is linked to one MemberWallet
    member_wallet = relationship("MemberWallet", back_populates="extensions")

    # One-to-One: Each MemberWalletExtension is linked to one WalletExtension
    wallet_extension = relationship("WalletExtensions", back_populates="member_wallet_extensions", uselist=False)
