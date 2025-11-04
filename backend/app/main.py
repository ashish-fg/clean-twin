"""Main FastAPI application for CleanTwin."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.inspections import router as inspections_router

# Create FastAPI application
app = FastAPI(
    title="CleanTwin API",
    description="API for building inspection management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API v1 prefix
app.include_router(inspections_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "CleanTwin API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
