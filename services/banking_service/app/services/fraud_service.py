from app.models.user import Transaction
from app.core.logger import get_logger, log_audit

logger = get_logger(__name__)

class FraudDetectionService:
    @staticmethod
    def check_transaction(account_id: int, amount: float):
        # Rule 1: High value transaction
        if amount > 100000:
            log_audit("FRAUD_ALERT", account_id, f"High value transaction detected: {amount}")
            return False, "Transaction exceeds high-value limit for automated processing"
            
        # Rule 2: Rapid transactions (simulated logic)
        # In a real app, check last 5 minutes of transactions from DB
        
        return True, "Success"

    @staticmethod
    def send_notification(user_id: int, action: str, amount: float):
        # Simulated Email Notification
        logger.info(f"NOTIFICATION: Sent email to User {user_id} for {action} of {amount}")
