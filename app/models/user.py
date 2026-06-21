from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Float, Date
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    EMPLOYEE = "Employee"
    CUSTOMER = "Customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    
    # Security Features
    is_mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    
    # Account Lockout fields
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    locked_until = Column(DateTime, nullable=True)

    accounts = relationship("Account", back_populates="owner")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    credit_cards = relationship("CreditCard", back_populates="owner")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")

class AccountType(str, enum.Enum):
    SAVINGS = "Savings"
    CURRENT = "Current"
    FIXED_DEPOSIT = "FixedDeposit"

class AccountStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    CLOSED = "Closed"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, index=True, nullable=False)
    balance = Column(Float, default=0.0)
    account_type = Column(Enum(AccountType), default=AccountType.SAVINGS)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # FD Specific fields
    interest_rate = Column(Float, nullable=True)
    maturity_date = Column(Date, nullable=True)

    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", foreign_keys="[Transaction.account_id]", back_populates="account")
    loans = relationship("Loan", back_populates="account")
    scheduled_payments = relationship("ScheduledPayment", back_populates="account")

class TransactionType(str, enum.Enum):
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER_SENT = "TransferSent"
    TRANSFER_RECEIVED = "TransferReceived"
    UPI_PAYMENT = "UPI"
    BILL_PAYMENT = "BillPayment"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    target_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType))
    description = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", foreign_keys=[account_id], back_populates="transactions")

class CreditCard(Base):
    __tablename__ = "credit_cards"
    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(16), unique=True, index=True)
    expiry_date = Column(String(5)) # MM/YY
    cvv = Column(String(3))
    credit_limit = Column(Float, default=100000.0)
    current_outstanding = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    owner = relationship("User", back_populates="credit_cards")

class ScheduledPayment(Base):
    __tablename__ = "scheduled_payments"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    recipient_account = Column(String(20))
    amount = Column(Float)
    frequency = Column(String(20)) # Daily, Weekly, Monthly
    next_payment_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    account = relationship("Account", back_populates="scheduled_payments")

class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    account_number = Column(String(20), nullable=False)
    bank_name = Column(String(255), default="Enterprise Bank")
    upi_id = Column(String(255), nullable=True)
    
    user = relationship("User")

class LoanStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=5.0)
    term_months = Column(Integer, nullable=False)
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    applied_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    account = relationship("Account", back_populates="loans")
