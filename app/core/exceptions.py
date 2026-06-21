from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional

class BankingException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details

async def banking_exception_handler(request: Request, exc: BankingException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    # Log the full exception here if needed
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An internal server error occurred",
            "message": str(exc) if True else None # Set to False in production
        }
    )
