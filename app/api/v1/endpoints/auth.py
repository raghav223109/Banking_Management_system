from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.api import deps
from app.schemas.user import UserOut, UserCreate, VerifyOTP, MFASetup
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.core.security import generate_mfa_secret, get_totp_uri
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    auth_service = AuthService(db)
    return auth_service.register_user(user_in)

@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    auth_service = AuthService(db)
    return auth_service.authenticate_user(form_data.username, form_data.password)

@router.post("/verify-mfa", response_model=Token)
def verify_mfa(user_id: int, otp_data: VerifyOTP, db: Session = Depends(deps.get_db)):
    auth_service = AuthService(db)
    return auth_service.verify_mfa_and_login(user_id, otp_data.otp)

@router.post("/refresh", response_model=Token)
def refresh_token(token: str, db: Session = Depends(deps.get_db)):
    auth_service = AuthService(db)
    return auth_service.rotate_refresh_token(token)

@router.post("/mfa/setup", response_model=MFASetup)
def setup_mfa(current_user=Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    secret = generate_mfa_secret()
    uri = get_totp_uri(secret, current_user.email)
    current_user.mfa_secret = secret
    current_user.is_mfa_enabled = True
    db.commit()
    return {"otp_uri": uri, "secret": secret}
