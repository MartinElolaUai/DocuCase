from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError


class AppError(Exception):
    """Custom application error."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def app_error_handler(request: Request, exc: AppError):
    """Handle custom application errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        }
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy/database errors."""
    import traceback
    error_details = str(exc)
    print(f"Database error: {exc}")
    print(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": f"Error de base de datos: {error_details}"
        }
    )


async def jwt_error_handler(request: Request, exc: JWTError):
    """Handle JWT errors."""
    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "message": "Token inválido o expirado"
        }
    )


async def generic_error_handler(request: Request, exc: Exception):
    """Handle generic/unexpected errors."""
    print(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Error interno del servidor"
        }
    )

