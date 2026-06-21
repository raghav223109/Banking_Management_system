from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .session import Base
import enum
from datetime import datetime

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
    owner_id = Column(Integer, index=True) # Reference to Auth Service User ID
    created_at = Column(DateTime, default=datetime.utcnow)
    interest_rate = Column(Float, nullable=True)
    maturity_date = Column(Date, nullable=True)

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
    expiry_date = Column(String(5))
    cvv = Column(String(3))
    credit_limit = Column(Float, default=100000.0)
    current_outstanding = Column(Float, default=0.0)
    owner_id = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)

class ScheduledPayment(Base):
    __tablename__ = "scheduled_payments"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    recipient_account = Column(String(20))
    amount = Column(Float)
    frequency = Column(String(20))
    next_payment_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    account = relationship("Account", back_populates="scheduled_payments")

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
    processed_by = Column(Integer, index=True)

    account = relationship("Account", back_populates="loans")
