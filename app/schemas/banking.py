from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.user import AccountType, AccountStatus, TransactionType, LoanStatus

# Account Schemas
class AccountBase(BaseModel):
    account_type: AccountType

class AccountCreate(AccountBase):
    pass

class AccountOut(AccountBase):
    id: int
    account_number: str
    balance: float
    status: AccountStatus
    created_at: datetime
    interest_rate: Optional[float] = None
    maturity_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    account_number: str

class TransferCreate(TransactionBase):
    from_account_number: str
    to_account_number: str

class TransactionOut(TransactionBase):
    id: int
    account_id: int
    target_account_id: Optional[int]
    transaction_type: TransactionType
    timestamp: datetime

    class Config:
        from_attributes = True

# Credit Card Schema
class CreditCardOut(BaseModel):
    card_number: str
    expiry_date: str
    credit_limit: float
    current_outstanding: float
    is_active: bool

    class Config:
        from_attributes = True

class ScheduledPaymentCreate(BaseModel):
    account_id: int
    recipient_account: str
    amount: float
    frequency: str # Daily, Weekly, Monthly
    next_payment_date: datetime

# Beneficiary Schemas
class BeneficiaryBase(BaseModel):
    name: str
    account_number: str
    bank_name: Optional[str] = "Enterprise Bank"
    upi_id: Optional[str] = None

class BeneficiaryCreate(BeneficiaryBase):
    pass

class BeneficiaryOut(BeneficiaryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Loan Schemas
class LoanBase(BaseModel):
    amount: float
    term_months: int

class LoanCreate(LoanBase):
    account_id: int

class LoanOut(LoanBase):
    id: int
    account_id: int
    interest_rate: float
    status: LoanStatus
    applied_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
