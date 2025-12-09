"""
Security middleware for FastAPI backend.
Implements security headers and other protective measures.
"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """
    
    def __init__(self, app: ASGIApp, csp_policy: str = None):
        super().__init__(app)
        # Default Content Security Policy
        if csp_policy:
            self.csp_policy = csp_policy
        else:
            self.csp_policy = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' http://localhost:* https://*.leanconstruction.ai; frame-ancestors 'self'; form-action 'self'; base-uri 'self';"
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        
        # Prevent caching of sensitive data
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        # Cross-Origin policies
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        # Add custom server timing header (helpful for debugging)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Remove server header to hide implementation details
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    Production should use Redis-based rate limiting.
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # In-memory storage (use Redis in production)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get current timestamp
        current_minute = int(time.time() / 60)
        key = f"{client_ip}:{current_minute}"
        
        # Count requests
        if key not in self.requests:
            self.requests[key] = 0
            # Clean old entries
            old_keys = [k for k in self.requests if not k.endswith(f":{current_minute}")]
            for old_key in old_keys:
                del self.requests[old_key]
        
        self.requests[key] += 1
        
        # Check rate limit
        if self.requests[key] > self.requests_per_minute:
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.requests_per_minute - self.requests[key])
        )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests for audit purposes.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Log request
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        logger.info(f"Request: {request.method} {request.url.path} Client: {client_host} User-Agent: {user_agent}")
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Response: {request.method} {request.url.path} Status: {response.status_code} Duration: {process_time:.3f}s")
        
        return response


def configure_cors(app, allowed_origins: list = None):
    """
    Configure CORS settings for the application.
    """
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "https://leanconstruction.ai",
            "https://www.leanconstruction.ai",
            "https://app.leanconstruction.ai",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        expose_headers=[
            "X-Process-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
        ],
        max_age=86400,  # Cache preflight for 24 hours
    )


def add_security_middleware(app, enable_rate_limit: bool = True, rate_limit: int = 100):
    """
    Add all security middleware to the FastAPI application.
    
    Usage:
        from app.middleware.security import add_security_middleware
        
        app = FastAPI()
        add_security_middleware(app)
    """
    # Configure CORS first
    configure_cors(app)
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add request logging (for audit)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add rate limiting
    if enable_rate_limit:
        app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit)
    
    logger.info("Security middleware configured successfully")


# Security utility functions
def sanitize_input(value: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    """
    if not value:
        return ""
    
    # Truncate to max length
    value = value[:max_length]
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Basic HTML entity encoding for common characters
    replacements = {
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "&": "&amp;",
    }
    for char, entity in replacements.items():
        value = value.replace(char, entity)
    
    return value


def validate_content_type(request: Request, allowed_types: list = None) -> bool:
    """
    Validate that the request has an allowed content type.
    """
    if allowed_types is None:
        allowed_types = ["application/json", "multipart/form-data"]
    
    content_type = request.headers.get("content-type", "").lower()
    return any(allowed in content_type for allowed in allowed_types)


def generate_nonce() -> str:
    """
    Generate a nonce for Content Security Policy.
    """
    import secrets
    return secrets.token_urlsafe(16)