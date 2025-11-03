"""
DPG - Decentralized Payment Gateway
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import asyncio

from database import engine, Base
from auth_routes import router as auth_router
from wallet_routes import router as wallet_router
from transaction_routes import router as transaction_router
from transaction_monitor import get_transaction_monitor

# Create database tables
print("🔧 Initializing database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")

# Initialize FastAPI app
app = FastAPI(
    title="DPG API",
    description="Decentralized Payment Gateway - Bridging TradFi with Crypto",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will configure properly later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

# Include wallet routes
app.include_router(wallet_router)

# Include transaction routes
app.include_router(transaction_router)


# Startup event - Start transaction monitor
@app.on_event("startup")
async def startup_event():
    """Start background services on app startup"""
    # Start transaction monitor in background
    monitor = get_transaction_monitor()
    asyncio.create_task(monitor.start())
    print("✅ Transaction monitor started - will check pending transactions every 30 seconds")


# Shutdown event - Stop transaction monitor
@app.on_event("shutdown")
async def shutdown_event():
    """Stop background services on app shutdown"""
    monitor = get_transaction_monitor()
    monitor.stop()
    print("🛑 Transaction monitor stopped")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "🚀 DPG Payment Gateway API",
        "status": "online",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "dpg-api",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/status")
async def api_status():
    """API status with feature flags"""
    return {
        "api_version": "v1",
        "features": {
            "auth": True,  # ✅ Authentication ACTIVE
            "wallets": True,  # ✅ Wallets ACTIVE
            "transactions": True,  # ✅ Transactions ACTIVE
            "trading": False,
            "cards": False,
            "merchant": False
        },
        "environment": os.getenv("NODE_ENV", "development"),
        "endpoints": {
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login",
            "profile": "/api/v1/auth/me"
        }
    }

# Error handlers
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,  # Changed to port 9000
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
