from fastapi import APIRouter, Depends
from app.api import deps
from app.models.user import User, UserRole
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(deps.get_current_user)):
    return current_user

@router.get("/admin-only", response_model=str)
def admin_only(admin_user: User = Depends(deps.RoleChecker([UserRole.ADMIN]))):
    return "Welcome, Admin!"

@router.get("/employee-or-admin", response_model=str)
def employee_or_admin(user: User = Depends(deps.RoleChecker([UserRole.ADMIN, UserRole.EMPLOYEE]))):
    return "Access granted to staff member."
