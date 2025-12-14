"""FastAPI middleware for logging, error handling, and monitoring."""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} - "
                f"Time: {process_time:.3f}s - "
                f"Path: {request.url.path}"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url} - "
                f"Error: {str(e)} - Time: {process_time:.3f}s"
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors globally."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error in {request.url.path}: {str(e)}", exc_info=True)
            
            # Return structured error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "path": str(request.url.path),
                    "method": request.method,
                    "timestamp": time.time()
                }
            )


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, calls_per_minute: int = 60):
        """Initialize rate limiting middleware."""
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.client_requests = {}  # In production, use Redis or similar
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting."""
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        cutoff_time = current_time - 60
        self.client_requests = {
            ip: requests for ip, requests in self.client_requests.items()
            if any(req_time > cutoff_time for req_time in requests)
        }
        
        # Update client requests
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []
        
        # Filter recent requests
        self.client_requests[client_ip] = [
            req_time for req_time in self.client_requests[client_ip]
            if req_time > cutoff_time
        ]
        
        # Check rate limit
        if len(self.client_requests[client_ip]) >= self.calls_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.calls_per_minute} requests per minute allowed",
                    "retry_after": 60
                }
            )
        
        # Add current request
        self.client_requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware for cache control headers."""
    
    def __init__(self, app, default_cache_seconds: int = 300):
        """Initialize cache control middleware."""
        super().__init__(app)
        self.default_cache_seconds = default_cache_seconds
        
        # Define cache policies for different endpoints
        self.cache_policies = {
            "/api/status": 60,  # 1 minute
            "/api/health": 30,  # 30 seconds
            "/api/dashboard/current": 300,  # 5 minutes
            "/api/data/historical": 3600,  # 1 hour
            "/api/insights/correlations": 1800,  # 30 minutes
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add cache control headers."""
        response = await call_next(request)
        
        # Determine cache duration
        path = request.url.path
        cache_seconds = self.cache_policies.get(path, self.default_cache_seconds)
        
        # Add cache headers for GET requests
        if request.method == "GET" and response.status_code == 200:
            response.headers["Cache-Control"] = f"public, max-age={cache_seconds}"
            response.headers["Expires"] = str(int(time.time() + cache_seconds))
        else:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting API metrics."""
    
    def __init__(self, app):
        """Initialize metrics middleware."""
        super().__init__(app)
        self.metrics = {
            "total_requests": 0,
            "requests_by_method": {},
            "requests_by_path": {},
            "response_times": [],
            "error_count": 0,
            "status_codes": {}
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Collect metrics."""
        start_time = time.time()
        
        # Update request counters
        self.metrics["total_requests"] += 1
        
        method = request.method
        self.metrics["requests_by_method"][method] = self.metrics["requests_by_method"].get(method, 0) + 1
        
        path = request.url.path
        self.metrics["requests_by_path"][path] = self.metrics["requests_by_path"].get(path, 0) + 1
        
        # Process request
        try:
            response = await call_next(request)
            
            # Record response metrics
            process_time = time.time() - start_time
            self.metrics["response_times"].append(process_time)
            
            # Keep only last 1000 response times
            if len(self.metrics["response_times"]) > 1000:
                self.metrics["response_times"] = self.metrics["response_times"][-1000:]
            
            # Count status codes
            status_code = response.status_code
            self.metrics["status_codes"][status_code] = self.metrics["status_codes"].get(status_code, 0) + 1
            
            # Count errors
            if status_code >= 400:
                self.metrics["error_count"] += 1
            
            return response
            
        except Exception as e:
            self.metrics["error_count"] += 1
            raise
    
    def get_metrics(self) -> dict:
        """Get current metrics."""
        response_times = self.metrics["response_times"]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        return {
            "total_requests": self.metrics["total_requests"],
            "error_count": self.metrics["error_count"],
            "error_rate": self.metrics["error_count"] / max(self.metrics["total_requests"], 1),
            "requests_by_method": self.metrics["requests_by_method"],
            "requests_by_path": dict(sorted(self.metrics["requests_by_path"].items(), key=lambda x: x[1], reverse=True)[:10]),
            "status_codes": self.metrics["status_codes"],
            "response_times": {
                "average": avg_response_time,
                "maximum": max_response_time,
                "minimum": min_response_time,
                "samples": len(response_times)
            }
        }


# Global metrics instance
metrics_middleware = MetricsMiddleware(None)