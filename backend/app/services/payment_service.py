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
        self.razorpay_key_id = settings.razorpay_key_id
    
    def create_order(
        self,
        amount: int,  # Amount in paise (₹150 = 15000)
        currency: str = "INR",
        receipt: str = "",
        notes: dict = None
    ) -> Dict:
        """
        Create Razorpay order for referral payment
        
        Args:
            amount: Amount in paise
            currency: Currency code
            receipt: Receipt ID
            notes: Additional notes
            
        Returns:
            Razorpay order details
        """
        try:
            order_data = {
                "amount": amount,
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {}
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"Created Razorpay order: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {e}")
            raise
    
    def verify_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature
        
        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Payment signature
            
        Returns:
            Boolean indicating signature validity
        """
        try:
            # Generate signature
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                settings.razorpay_key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(generated_signature, razorpay_signature)
            
            if is_valid:
                logger.info(f"Payment signature verified for order {razorpay_order_id}")
            else:
                logger.warning(f"Invalid payment signature for order {razorpay_order_id}")
            
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
