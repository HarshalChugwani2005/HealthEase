from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId as ObjectId
from enum import Enum


class TransactionType(str, Enum):
    """Wallet transaction type enumeration"""
    CREDIT = "credit"
    DEBIT = "debit"
    WITHDRAWAL = "withdrawal"
    REFERRAL_EARNING = "referral_earning"


class PayoutStatus(str, Enum):
    """Payout request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"


class Wallet(Document):
    """Digital wallet model for hospitals"""
    hospital_id: ObjectId = Field(unique=True, index=True)
    balance: float = 0.0
    total_earned: float = 0.0
    total_withdrawn: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "wallets"
        indexes = [
            "hospital_id"
        ]
    
    async def credit(self, amount: float):
        """Credit wallet"""
        self.balance += amount
        self.total_earned += amount
        self.updated_at = datetime.utcnow()
        await self.save()
    
    async def debit(self, amount: float):
        """Debit wallet"""
        if self.balance < amount:
            raise ValueError("Insufficient wallet balance")
        self.balance -= amount
        self.total_withdrawn += amount
        self.updated_at = datetime.utcnow()
        await self.save()
    
    class Config:
        json_schema_extra = {
            "example": {
                "balance": 5500.0,
                "total_earned": 12000.0,
                "total_withdrawn": 6500.0
            }
        }


class WalletTransaction(Document):
    """Wallet transaction log model"""
    wallet_id: ObjectId = Field(index=True)
    referral_id: Optional[ObjectId] = None
    transaction_type: TransactionType
    amount: float
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "wallet_transactions"
        indexes = [
            "wallet_id",
            "transaction_type",
            "created_at",
            [("wallet_id", 1), ("created_at", -1)]
        ]
    
    @property
    def balance_after(self) -> float:
        """Calculate balance after transaction"""
        # This should be set during transaction creation
        return 0.0  # Placeholder
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_type": "credit",
                "amount": 55.0,
                "description": "Referral payment from Hospital A to Hospital B"
            }
        }


class PayoutRequest(Document):
    """Payout request model for hospitals"""
    wallet_id: ObjectId = Field(index=True)
    hospital_id: ObjectId = Field(index=True)
    amount: float
    account_holder_name: str
    account_number: str
    ifsc_code: str
    bank_name: str
    status: PayoutStatus = PayoutStatus.PENDING
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    admin_notes: Optional[str] = None
    
    class Settings:
        name = "payout_requests"
        indexes = [
            "wallet_id",
            "hospital_id",
            "status",
            "requested_at"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 5000.0,
                "account_holder_name": "City Hospital",
                "account_number": "1234567890",
                "ifsc_code": "HDFC0001234",
                "bank_name": "HDFC Bank",
                "status": "pending"
            }
        }
