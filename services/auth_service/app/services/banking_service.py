from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.banking_repository import BankingRepository
from app.models.user import TransactionType, AccountStatus, LoanStatus, UserRole
from app.schemas.banking import AccountCreate, TransactionCreate, TransferCreate, LoanCreate
from datetime import datetime
from app.core.logger import log_audit
from app.services.fraud_service import FraudDetectionService
from app.services.analytics_service import AnalyticsService

class BankingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BankingRepository(db)

    def deposit(self, data: TransactionCreate):
        account = self.repo.get_account_by_number(data.account_number)
        if not account or account.status != AccountStatus.ACTIVE:
            raise HTTPException(status_code=404, detail="Active account not found")

        # Fraud Check
        is_safe, msg = FraudDetectionService.check_transaction(account.id, data.amount)
        if not is_safe:
            raise HTTPException(status_code=403, detail=msg)

        try:
            account.balance += data.amount
            self.repo.create_transaction(
                account.id, data.amount, TransactionType.DEPOSIT, data.description or "Cash Deposit"
            )
            self.db.commit()
            log_audit("DEPOSIT", account.owner_id, f"Amount: {data.amount} to {account.account_number}")
            FraudDetectionService.send_notification(account.owner_id, "Deposit", data.amount)
            return account
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Transaction failed")

    def withdraw(self, data: TransactionCreate):
        account = self.repo.get_account_by_number(data.account_number)
        if not account or account.status != AccountStatus.ACTIVE:
            raise HTTPException(status_code=404, detail="Active account not found")
        
        # Fraud Check
        is_safe, msg = FraudDetectionService.check_transaction(account.id, data.amount)
        if not is_safe:
            raise HTTPException(status_code=403, detail=msg)

        if account.balance < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        try:
            account.balance -= data.amount
            self.repo.create_transaction(
                account.id, data.amount, TransactionType.WITHDRAWAL, data.description or "Cash Withdrawal"
            )
            self.db.commit()
            log_audit("WITHDRAWAL", account.owner_id, f"Amount: {data.amount} from {account.account_number}")
            FraudDetectionService.send_notification(account.owner_id, "Withdrawal", data.amount)
            return account
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Transaction failed")

    def transfer(self, data: TransferCreate):
        from_acc = self.repo.get_account_by_number(data.from_account_number)
        to_acc = self.repo.get_account_by_number(data.to_account_number)

        if not from_acc or from_acc.status != AccountStatus.ACTIVE:
            raise HTTPException(status_code=404, detail="Source account not found or inactive")
        if not to_acc or to_acc.status != AccountStatus.ACTIVE:
            raise HTTPException(status_code=404, detail="Destination account not found or inactive")

        if from_acc.balance < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        try:
            # Atomic transfer
            from_acc.balance -= data.amount
            to_acc.balance += data.amount

            self.repo.create_transaction(
                from_acc.id, data.amount, TransactionType.TRANSFER_SENT, 
                data.description or f"Transfer to {to_acc.account_number}", target_id=to_acc.id
            )
            self.repo.create_transaction(
                to_acc.id, data.amount, TransactionType.TRANSFER_RECEIVED, 
                data.description or f"Transfer from {from_acc.account_number}", target_id=from_acc.id
            )
            self.db.commit()
            log_audit("TRANSFER", from_acc.owner_id, f"Amount: {data.amount} to {to_acc.account_number}")
            return from_acc
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Transfer failed")

    def approve_loan(self, loan_id: int, admin_id: int, approve: bool):
        loan = self.repo.get_loan(loan_id)
        if not loan or loan.status != LoanStatus.PENDING:
            raise HTTPException(status_code=404, detail="Pending loan not found")

        try:
            if approve:
                loan.status = LoanStatus.APPROVED
                # Credit the account
                loan.account.balance += loan.amount
                self.repo.create_transaction(
                    loan.account_id, loan.amount, TransactionType.DEPOSIT, f"Loan Disbursement: {loan.id}"
                )
            else:
                loan.status = LoanStatus.REJECTED
            
            loan.processed_at = datetime.utcnow()
            loan.processed_by = admin_id
            self.db.commit()
            return loan
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Workflow failed")

    def close_account(self, account_number: str):
        account = self.repo.get_account_by_number(account_number)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if account.balance != 0:
            raise HTTPException(status_code=400, detail="Account balance must be zero before closure")

        account.status = AccountStatus.CLOSED
        self.db.commit()
        return account
