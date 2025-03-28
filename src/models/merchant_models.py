from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    TIMESTAMP,
    Enum,
    Float
)

from sqlalchemy.orm import relationship
from core.database import Base

from sqlalchemy.sql import func
from uuid import uuid4




class Merchant(Base):
    __tablename__ = "merchants"

    merchant_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    mobile_number = Column(String(10), ForeignKey('members.mobile_number', ondelete="CASCADE"), nullable=False)

    business_name = Column(String(155), nullable=False)
    business_type = Column(String(155), nullable=False)
    
    discount = Column(Float, nullable=True)
    merchant_wallet = Column(Float, nullable=False, server_default="0.00", default=0.00)
    reward_points = Column(Float, nullable=False, server_default="0.00", default=0.00)

    #qr_code_url = Column(String(3000), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    member = relationship("Member", back_populates="merchant")
    details = relationship("MerchantDetails", uselist=False, back_populates="merchant", cascade="all, delete-orphan")

    
    # Relationship to MerchantReferral (One-to-One)
    merchant_referral = relationship("MerchantReferral", back_populates="merchant", uselist=False, cascade="all, delete-orphan")

    # Relationship to MerchantPurchaseHistory (One-to-Many)
    merchant_purchases = relationship("MerchantPurchaseHistory", back_populates="merchant", cascade="all, delete-orphan")




class MerchantDetails(Base):
    __tablename__ = "merchant_details"

    merchant_id = Column(String(36), ForeignKey("merchants.merchant_id", ondelete="CASCADE"), primary_key=True, index=True)
    
    latitude = Column(String(100), nullable=False)
    longitude = Column(String(100), nullable=False)
    
    region = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)
    municipality_city = Column(String(100), nullable=False)
    barangay = Column(String(100), nullable=False)
    street = Column(String(100), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship
    merchant = relationship("Merchant", back_populates="details")



class MerchantReferral(Base):
    __tablename__ = "merchant_referrals"

    referral_id = Column(String(36), primary_key=True, index=True, default = lambda: str(uuid4()))

    # merchant direct referrer
    referred_by = Column(String(12), ForeignKey('members.referral_id', ondelete="CASCADE"), nullable=False)

    # merchant
    referred_merchant = Column(String(36), ForeignKey("merchants.merchant_id", ondelete="CASCADE"), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    referrer = relationship("Member", back_populates="merchant_referrals_made", foreign_keys=[referred_by])
    merchant = relationship("Merchant", back_populates="merchant_referral")


class MerchantPurchaseHistory(Base):
    __tablename__ = "merchant_purchases"

    purchase_id = Column(String(36), primary_key=True, index=True, default = lambda: str(uuid4()))

    # merchant
    merchant_id = Column(String(36), ForeignKey("merchants.merchant_id", ondelete="CASCADE"), nullable=False)

    # member
    member_id = Column(String(36), ForeignKey("members.member_id", ondelete="CASCADE"), nullable=False)

    amount = Column(Float, nullable=False)

    reference_id = Column(String(120), nullable=False)

    extra_metadata = Column(String(255), nullable=True)

    description = Column(String(255), nullable=True)


    status = Column(Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, server_default='pending', default='pending')

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="merchant_purchases")
    member = relationship("Member", back_populates="member_purchases")



    