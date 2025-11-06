"""
Main FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.errors import APIError
from app.api.v1 import api_router

# Configure structured logging
setup_logging(
    log_level=settings.ENVIRONMENT == "development" and "DEBUG" or "INFO",
    json_logs=settings.ENVIRONMENT != "development"
)
logger = get_logger(__name__)

# Initialize rate limiter
#limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
#app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware for logging and versioning
#app.add_middleware(RequestLoggingMiddleware)
#app.add_middleware(APIVersionMiddleware)

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors with details"""
    logger.error(f"Validation error on {request.method} {request.url.path}")
    logger.error(f"Validation details: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Santé Medical API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

logger.info(f"Application started - {settings.PROJECT_NAME} v{settings.VERSION}")