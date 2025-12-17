import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        print(f"{request.method} {request.url.path} {response.status_code} - {duration:.0f}ms")
        
        return response

