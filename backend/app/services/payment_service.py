import razorpay
from app.config import settings
from app.models.referral import Referral
from typing import Dict
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for Razorpay payment integration"""
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )
    
    async def create_order(
        self,
        amount: int,  # Amount in paise (₹150 = 15000)
        patient_id: str,
        referral_id: str
    ) -> Dict:
        """
        Create Razorpay order for referral payment
        
        Args:
            amount: Amount in paise
            patient_id: Patient ID
            referral_id: Referral ID
            
        Returns:
            Razorpay order details
        """
        try:
            order_data = {
                "amount": amount,
                "currency": "INR",
                "receipt": f"referral_{referral_id}",
                "notes": {
                    "patient_id": patient_id,
                    "referral_id": referral_id
                }
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"Created Razorpay order: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {e}")
            raise
    
    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Payment signature
            
        Returns:
            Boolean indicating signature validity
        """
        try:
            # Generate signature
            message = f"{order_id}|{payment_id}"
            generated_signature = hmac.new(
                settings.razorpay_key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(generated_signature, signature)
            
            if is_valid:
                logger.info(f"Payment signature verified for order {order_id}")
            else:
                logger.warning(f"Invalid payment signature for order {order_id}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying payment signature: {e}")
            return False
    
    async def fetch_payment(self, payment_id: str) -> Dict:
        """
        Fetch payment details from Razorpay
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            Payment details
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Failed to fetch payment {payment_id}: {e}")
            raise


# Global payment service instance
payment_service = PaymentService()
