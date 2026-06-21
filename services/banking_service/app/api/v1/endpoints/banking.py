from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.user import User, UserRole, Account, TransactionType
from app.schemas.banking import (
    AccountCreate, AccountOut, TransactionCreate, TransferCreate, 
    TransactionOut, BeneficiaryCreate, BeneficiaryOut, LoanCreate, LoanOut,
    CreditCardOut
)
from app.services.banking_service import BankingService
from app.repositories.banking_repository import BankingRepository
from app.utils.pagination import Page, Params, paginate
from app.utils.calculators import calculate_emi
from app.utils.reporting import ReportGenerator

router = APIRouter()

@router.get("/accounts/{account_number}/statement/pdf")
def export_pdf(account_number: str, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    acc = BankingRepository(db).get_account_by_number(account_number)
    if not acc or acc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    pdf_content = ReportGenerator.generate_statement_pdf(current_user.full_name, account_number, acc.transactions)
    return Response(content=pdf_content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=statement_{account_number}.pdf"})

@router.get("/accounts/{account_number}/statement/excel")
def export_excel(account_number: str, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    acc = BankingRepository(db).get_account_by_number(account_number)
    if not acc or acc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    excel_content = ReportGenerator.generate_statement_excel(current_user.full_name, account_number, acc.transactions)
    return Response(content=excel_content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=statement_{account_number}.xlsx"})

@router.post("/upi/pay", response_model=TransactionOut)
def upi_payment(vpa: str, amount: float, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    # Simulate UPI payment from first available account
    acc = current_user.accounts[0]
    if acc.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    service = BankingService(db)
    # Reusing deposit/withdraw logic for simulation
    data = TransactionCreate(account_number=acc.account_number, amount=amount, description=f"UPI Payment to {vpa}")
    service.withdraw(data)
    # Manually change type for simulation
    last_t = acc.transactions[-1]
    last_t.transaction_type = TransactionType.UPI_PAYMENT
    db.commit()
    return last_t

@router.get("/credit-cards", response_model=List[CreditCardOut])
def get_my_cards(current_user: User = Depends(deps.get_current_user)):
    return current_user.credit_cards

@router.post("/accounts", response_model=AccountOut)
def create_account(account_in: AccountCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    repo = BankingRepository(db)
    return repo.create_account(current_user.id, account_in)

@router.get("/accounts", response_model=List[AccountOut])
def get_my_accounts(db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    repo = BankingRepository(db)
    return repo.get_accounts_by_user(current_user.id)
@router.post("/deposit", response_model=AccountOut)
def deposit(data: TransactionCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = BankingService(db)
    acc = BankingRepository(db).get_account_by_number(data.account_number)
    if not acc or (acc.owner_id != current_user.id and current_user.role == UserRole.CUSTOMER):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return service.deposit(data)

@router.post("/withdraw", response_model=AccountOut)
def withdraw(data: TransactionCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = BankingService(db)
    acc = BankingRepository(db).get_account_by_number(data.account_number)
    if not acc or (acc.owner_id != current_user.id and current_user.role == UserRole.CUSTOMER):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return service.withdraw(data)

@router.post("/transfer", response_model=AccountOut)
def transfer(data: TransferCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = BankingService(db)
    acc = BankingRepository(db).get_account_by_number(data.from_account_number)
    if not acc or acc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return service.transfer(data)

@router.get("/accounts/{account_number}/transactions", response_model=Page[TransactionOut])
def get_transaction_history(
    account_number: str, 
    params: Params = Depends(),
    t_type: Optional[TransactionType] = None,
    db: Session = Depends(deps.get_db), 
    current_user: User = Depends(deps.get_current_user)
):
    from app.models.user import Transaction
    acc = BankingRepository(db).get_account_by_number(account_number)
    if not acc or (acc.owner_id != current_user.id and current_user.role == UserRole.CUSTOMER):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    query = db.query(Transaction).filter(Transaction.account_id == acc.id)
    if t_type:
        query = query.filter(Transaction.transaction_type == t_type)
        
    return paginate(query, params, TransactionOut)

@router.post("/beneficiaries", response_model=BeneficiaryOut)
def add_beneficiary(data: BeneficiaryCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    repo = BankingRepository(db)
    return repo.add_beneficiary(current_user.id, data)

@router.post("/loans/apply", response_model=LoanOut)
def apply_loan(data: LoanCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    from app.models.user import Account
    acc = db.query(Account).filter(Account.id == data.account_id).first()
    if not acc or acc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized or invalid account")
    repo = BankingRepository(db)
    return repo.apply_loan(data)

@router.post("/loans/{loan_id}/approve", response_model=LoanOut)
def approve_loan(loan_id: int, approve: bool, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.RoleChecker([UserRole.ADMIN, UserRole.EMPLOYEE]))):
    service = BankingService(db)
    return service.approve_loan(loan_id, current_user.id, approve)

@router.post("/accounts/{account_number}/close", response_model=AccountOut)
def close_account(account_number: str, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = BankingService(db)
    acc = BankingRepository(db).get_account_by_number(account_number)
    if not acc or (acc.owner_id != current_user.id and current_user.role == UserRole.CUSTOMER):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return service.close_account(account_number)
