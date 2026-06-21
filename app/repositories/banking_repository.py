from sqlalchemy.orm import Session
from app.models.user import Account, Transaction, Beneficiary, Loan, TransactionType, AccountStatus, LoanStatus
from app.schemas.banking import AccountCreate, TransactionCreate, BeneficiaryCreate, LoanCreate
import random
import string

class BankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def generate_account_number(self):
        return ''.join(random.choices(string.digits, k=12))

    def create_account(self, user_id: int, obj_in: AccountCreate) -> Account:
        db_obj = Account(
            account_number=self.generate_account_number(),
            account_type=obj_in.account_type,
            owner_id=user_id,
            balance=0.0,
            status=AccountStatus.ACTIVE
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_account_by_number(self, account_number: str) -> Account:
        return self.db.query(Account).filter(Account.account_number == account_number).first()

    def get_accounts_by_user(self, user_id: int):
        return self.db.query(Account).filter(Account.owner_id == user_id).all()

    def create_transaction(self, account_id: int, amount: float, t_type: TransactionType, desc: str, target_id: int = None) -> Transaction:
        db_obj = Transaction(
            account_id=account_id,
            amount=amount,
            transaction_type=t_type,
            description=desc,
            target_account_id=target_id
        )
        self.db.add(db_obj)
        return db_obj

    def add_beneficiary(self, user_id: int, obj_in: BeneficiaryCreate) -> Beneficiary:
        db_obj = Beneficiary(
            user_id=user_id,
            name=obj_in.name,
            account_number=obj_in.account_number,
            bank_name=obj_in.bank_name
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_beneficiaries(self, user_id: int):
        return self.db.query(Beneficiary).filter(Beneficiary.user_id == user_id).all()

    def apply_loan(self, obj_in: LoanCreate) -> Loan:
        db_obj = Loan(
            account_id=obj_in.account_id,
            amount=obj_in.amount,
            term_months=obj_in.term_months,
            status=LoanStatus.PENDING
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_loan(self, loan_id: int) -> Loan:
        return self.db.query(Loan).filter(Loan.id == loan_id).first()
    
    def get_pending_loans(self):
        return self.db.query(Loan).filter(Loan.status == LoanStatus.PENDING).all()
