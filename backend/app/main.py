from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError
from datetime import datetime

from app.config import settings
from app.database import engine, Base
from app.middleware.error_handler import (
    AppError, app_error_handler, http_exception_handler,
    sqlalchemy_error_handler, jwt_error_handler, generic_error_handler
)
from app.middleware.request_logger import RequestLoggerMiddleware

# Import routers
from app.routers import (
    auth,
    users,
    groups,
    applications,
    features,
    test_cases,
    test_requests,
    pipelines,
    dashboard,
    uploads,
)

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="DashCase API",
    description="API para gestión y documentación de casos de prueba",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logger middleware
app.add_middleware(RequestLoggerMiddleware)

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(JWTError, jwt_error_handler)
app.add_exception_handler(Exception, generic_error_handler)


# Health check endpoint
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(features.router, prefix="/api")
app.include_router(test_cases.router, prefix="/api")
app.include_router(test_requests.router, prefix="/api")
app.include_router(pipelines.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")

# Static files for uploaded images (e.g., test request references)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    print("Database connected")
    print(f"Server running on http://localhost:{settings.PORT}")
    print(f"API available at http://localhost:{settings.PORT}/api")
    print(f"Docs available at http://localhost:{settings.PORT}/api/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    print("Shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development"
    )

