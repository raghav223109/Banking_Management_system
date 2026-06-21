from apscheduler.schedulers.background import BackgroundScheduler
from app.db.session import SessionLocal
from app.models.user import Account, AccountType, Transaction, TransactionType
from app.core.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

def calculate_monthly_interest():
    db = SessionLocal()
    try:
        logger.info("Starting monthly interest calculation task")
        savings_accounts = db.query(Account).filter(
            Account.account_type == AccountType.SAVINGS,
            Account.status == "Active"
        ).all()
        
        for acc in savings_accounts:
            # Simple 0.5% monthly interest (approx 6% yearly)
            interest = acc.balance * 0.005
            if interest > 0:
                acc.balance += interest
                t = Transaction(
                    account_id=acc.id,
                    amount=interest,
                    transaction_type=TransactionType.DEPOSIT,
                    description="Monthly Interest Credit"
                )
                db.add(t)
        db.commit()
        logger.info("Interest calculation completed")
    except Exception as e:
        logger.error(f"Error in interest task: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule interest calculation on the 1st of every month at midnight
    scheduler.add_job(calculate_monthly_interest, 'cron', day=1, hour=0, minute=0)
    # For demo purposes, we could run it every 24 hours
    # scheduler.add_job(calculate_monthly_interest, 'interval', hours=24)
    scheduler.start()
    return scheduler
