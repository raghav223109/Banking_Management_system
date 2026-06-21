from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_otp, generate_mfa_secret
from app.core.config import settings
from app.schemas.user import UserCreate, VerifyOTP
from app.schemas.token import Token
from app.models.user import RefreshToken
from sqlalchemy.orm import Session

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_in: UserCreate):
        user = self.user_repo.get_by_email(user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        new_user = self.user_repo.create(user_in)
        return new_user

    def authenticate_user(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            if user:
                self.user_repo.increment_failed_attempts(user, settings.MAX_FAILED_ATTEMPTS, settings.LOCKOUT_TIME_MINUTES)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(status_code=403, detail="Account locked")

        # If MFA is enabled, we don't return tokens yet
        if user.is_mfa_enabled:
            return {"mfa_required": True, "user_id": user.id}

        return self.generate_tokens(user)

    def verify_mfa_and_login(self, user_id: int, otp: str):
        user = self.user_repo.get(user_id)
        if not user or not verify_otp(user.mfa_secret, otp):
             raise HTTPException(status_code=401, detail="Invalid OTP")
        
        return self.generate_tokens(user)

    def generate_tokens(self, user) -> Token:
        access_token = create_access_token(user.id)
        refresh_token_str, expires_at = create_refresh_token(user.id)
        
        # Save refresh token (supporting rotation)
        db_rf = RefreshToken(token=refresh_token_str, user_id=user.id, expires_at=expires_at)
        self.db.add(db_rf)
        self.db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer"
        )

    def rotate_refresh_token(self, old_token_str: str):
        rf = self.db.query(RefreshToken).filter(RefreshToken.token == old_token_str, RefreshToken.is_revoked == False).first()
        if not rf or rf.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        # Revoke old token
        rf.is_revoked = True
        self.db.commit()

        # Generate new pair
        return self.generate_tokens(rf.user)
