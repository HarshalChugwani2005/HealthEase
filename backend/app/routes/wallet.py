from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.models.wallet import Wallet, WalletTransaction, TransactionType, PayoutRequest, PayoutStatus
from app.models.hospital import Hospital
from app.middleware.auth import get_hospital_user
from app.models.user import User
from bson import ObjectId
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["Wallet Management"])


class PayoutRequestSchema(BaseModel):
    """Schema for payout request"""
    amount: float
    account_holder_name: str
    account_number: str
    ifsc_code: str
    bank_name: str


@router.get("/balance")
async def get_wallet_balance(current_user: User = Depends(get_hospital_user)):
    """
    Get current wallet balance for hospital
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        # Get or create wallet
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital_id)
        
        if not wallet:
            wallet = Wallet(hospital_id=hospital_id)
            await wallet.insert()
        
        hospital = await Hospital.get(hospital_id)
        
        return {
            "hospital_name": hospital.name if hospital else "Unknown",
            "wallet_id": str(wallet.id),
            "balance": wallet.balance,
            "total_earned": wallet.total_earned,
            "total_withdrawn": wallet.total_withdrawn,
            "last_updated": wallet.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get wallet balance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/transactions")
async def get_wallet_transactions(
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_hospital_user)
):
    """
    Get wallet transaction history
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        # Get wallet
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital_id)
        
        if not wallet:
            return {
                "transactions": [],
                "count": 0
            }
        
        # Get transactions
        transactions = await WalletTransaction.find(
            WalletTransaction.wallet_id == wallet.id
        ).sort("-created_at").skip(skip).limit(limit).to_list()
        
        result = []
        for txn in transactions:
            result.append({
                "id": str(txn.id),
                "type": txn.transaction_type,
                "amount": txn.amount,
                "balance_after": txn.balance_after,
                "description": txn.description,
                "referral_id": str(txn.referral_id) if txn.referral_id else None,
                "created_at": txn.created_at.isoformat()
            })
        
        return {
            "transactions": result,
            "count": len(result),
            "limit": limit,
            "skip": skip
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get transactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/request-payout")
async def request_payout(
    payout_data: PayoutRequestSchema,
    current_user: User = Depends(get_hospital_user)
):
    """
    Request payout from wallet to bank account
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        # Get wallet
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital_id)
        
        if not wallet or wallet.balance < payout_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance"
            )
        
        # Minimum payout check
        if payout_data.amount < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum payout amount is ₹100"
            )
        
        # Create payout request
        payout_request = PayoutRequest(
            wallet_id=wallet.id,
            hospital_id=hospital_id,
            amount=payout_data.amount,
            account_holder_name=payout_data.account_holder_name,
            account_number=payout_data.account_number,
            ifsc_code=payout_data.ifsc_code,
            bank_name=payout_data.bank_name,
            status=PayoutStatus.PENDING,
            requested_at=datetime.utcnow()
        )
        await payout_request.insert()
        
        logger.info(f"Payout request created: {payout_request.id} for ₹{payout_data.amount}")
        
        return {
            "message": "Payout request submitted successfully",
            "payout_id": str(payout_request.id),
            "amount": payout_data.amount,
            "status": PayoutStatus.PENDING,
            "estimated_processing_days": "3-5 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request payout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/payout-requests")
async def get_payout_requests(
    current_user: User = Depends(get_hospital_user)
):
    """
    Get all payout requests for hospital
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        payouts = await PayoutRequest.find(
            PayoutRequest.hospital_id == hospital_id
        ).sort("-requested_at").to_list()
        
        result = []
        for payout in payouts:
            result.append({
                "id": str(payout.id),
                "amount": payout.amount,
                "status": payout.status,
                "account_holder": payout.account_holder_name,
                "account_number": f"****{payout.account_number[-4:]}",
                "bank_name": payout.bank_name,
                "requested_at": payout.requested_at.isoformat(),
                "processed_at": payout.processed_at.isoformat() if payout.processed_at else None,
                "admin_notes": payout.admin_notes if payout.status == PayoutStatus.REJECTED else None
            })
        
        return {
            "payout_requests": result,
            "count": len(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get payout requests error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/statistics")
async def get_wallet_statistics(
    current_user: User = Depends(get_hospital_user)
):
    """
    Get wallet statistics and insights
    """
    try:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital"
            )
        
        hospital_id = ObjectId(current_user.hospital_id)
        
        # Get wallet
        wallet = await Wallet.find_one(Wallet.hospital_id == hospital_id)
        
        if not wallet:
            return {
                "current_balance": 0,
                "total_earned": 0,
                "total_withdrawn": 0,
                "pending_payouts": 0,
                "referral_earnings": 0,
                "transaction_count": 0,
                "avg_txn_amount": 0,
                "monthly_earnings": [],
                "earnings_by_type": {}
            }
        
        # Pending payouts
        pending_payouts = await PayoutRequest.find(
            PayoutRequest.wallet_id == wallet.id,
            PayoutRequest.status == PayoutStatus.PENDING
        ).sum(PayoutRequest.amount) or 0
        
        # Transaction analysis
        transactions = await WalletTransaction.find(
            WalletTransaction.wallet_id == wallet.id
        ).to_list()
        
        referral_earnings = sum(
            t.amount for t in transactions 
            if t.transaction_type == TransactionType.CREDIT and t.referral_id
        )
        
        total_txn_amount = sum(t.amount for t in transactions)
        avg_txn_amount = total_txn_amount / len(transactions) if transactions else 0
        
        # Monthly earnings
        monthly_earnings = {}
        for txn in transactions:
            if txn.transaction_type == TransactionType.CREDIT:
                month = txn.created_at.strftime("%Y-%m")
                monthly_earnings[month] = monthly_earnings.get(month, 0) + txn.amount
        
        # Earnings by type (e.g. from referrals)
        earnings_by_type = {
            "referrals": referral_earnings,
            "other_credits": wallet.total_earned - referral_earnings
        }
        
        return {
            "current_balance": wallet.balance,
            "total_earned": wallet.total_earned,
            "total_withdrawn": wallet.total_withdrawn,
            "pending_payouts": pending_payouts,
            "referral_earnings": referral_earnings,
            "transaction_count": len(transactions),
            "avg_txn_amount": round(avg_txn_amount, 2),
            "monthly_earnings": sorted(
                [{"month": k, "earnings": v} for k, v in monthly_earnings.items()],
                key=lambda x: x['month']
            ),
            "earnings_by_type": earnings_by_type
        }
        
    except Exception as e:
        logger.error(f"Wallet statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
