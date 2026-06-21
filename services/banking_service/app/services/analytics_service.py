from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import Transaction, Account, TransactionType

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_account_summary(self, account_id: int):
        total_deposits = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == TransactionType.DEPOSIT
        ).scalar() or 0.0

        total_withdrawals = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == TransactionType.WITHDRAWAL
        ).scalar() or 0.0

        transaction_count = self.db.query(func.count(Transaction.id)).filter(
            Transaction.account_id == account_id
        ).scalar()

        return {
            "total_deposited": total_deposits,
            "total_withdrawn": total_withdrawals,
            "transaction_count": transaction_count,
            "net_flow": total_deposits - total_withdrawals
        }
