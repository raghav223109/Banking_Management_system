import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if not exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging format
log_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# System Logger
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler("logs/system.log", maxBytes=10485760, backupCount=5)
    ]
)

# Audit Logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
audit_handler = RotatingFileHandler("logs/audit.log", maxBytes=10485760, backupCount=10)
audit_handler.setFormatter(logging.Formatter("%(asctime)s - AUDIT - %(message)s"))
audit_logger.addHandler(audit_handler)

def log_audit(action: str, user_id: int, details: str):
    audit_logger.info(f"User: {user_id} | Action: {action} | Details: {details}")

def get_logger(name: str):
    return logging.getLogger(name)
