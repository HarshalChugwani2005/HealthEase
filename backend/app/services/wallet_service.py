from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.models.referral import Referral
from bson import ObjectId
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WalletService:
    """Service for wallet operations"""
    
    @staticmethod
    async def get_or_create_wallet(hospital_id: ObjectId) -> Wallet:
        """
        Get wallet for hospital, create if doesn't exist
        
        Args:
            hospital_id: Hospital ObjectId
            
        Returns:
            Wallet object
        """
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital_id)
        
        if not wallet:
            wallet = Wallet(hospital_id=hospital_id)
            await wallet.insert()
            logger.info(f"Created new wallet for hospital {hospital_id}")
        
        return wallet
    
    @staticmethod
    async def credit_wallet(
        hospital_id: ObjectId,
        amount: float,
        description: str,
        referral_id: Optional[ObjectId] = None
    ) -> WalletTransaction:
        """
        Credit amount to hospital wallet
        
        Args:
            hospital_id: Hospital ObjectId
            amount: Amount to credit
            description: Transaction description
            referral_id: Optional referral ID
            
        Returns:
            WalletTransaction object
        """
        wallet = await WalletService.get_or_create_wallet(hospital_id)
        await wallet.credit(amount)
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            referral_id=referral_id,
            transaction_type=TransactionType.CREDIT,
            amount=amount,
            description=description
        )
        await transaction.insert()
        
        logger.info(f"Credited ₹{amount} to wallet {wallet.id}")
        return transaction
    
    @staticmethod
    async def debit_wallet(
        hospital_id: ObjectId,
        amount: float,
        description: str
    ) -> WalletTransaction:
        """
        Debit amount from hospital wallet
        
        Args:
            hospital_id: Hospital ObjectId
            amount: Amount to debit
            description: Transaction description
            
        Returns:
            WalletTransaction object
            
        Raises:
            ValueError: If insufficient balance
        """
        wallet = await WalletService.get_or_create_wallet(hospital_id)
        await wallet.debit(amount)
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.DEBIT,
            amount=amount,
            description=description
        )
        await transaction.insert()
        
        logger.info(f"Debited ₹{amount} from wallet {wallet.id}")
        return transaction
    
    @staticmethod
    async def process_referral_payment(
        referral: Referral,
        from_hospital_share: float,
        to_hospital_share: float
    ):
        """
        Process payment distribution for referral
        
        Args:
            referral: Referral object
            from_hospital_share: Share for referring hospital
            to_hospital_share: Share for accepting hospital
        """
        # Credit from_hospital
        await WalletService.credit_wallet(
            hospital_id=referral.from_hospital_id,
            amount=from_hospital_share,
            description=f"Referral payment - referring hospital (Referral #{referral.id})",
            referral_id=referral.id
        )
        
        # Credit to_hospital
        await WalletService.credit_wallet(
            hospital_id=referral.to_hospital_id,
            amount=to_hospital_share,
            description=f"Referral payment - accepting hospital (Referral #{referral.id})",
            referral_id=referral.id
        )
        
        logger.info(
            f"Processed referral payment: From Hospital ₹{from_hospital_share}, "
            f"To Hospital ₹{to_hospital_share}"
        )
