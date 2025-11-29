from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, db
from app.routes import auth, hospital, patient, admin
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic AI Hospital Management & Patient Flow Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    try:
        await connect_to_mongo()
        if db.connected:
            logger.info("Application startup complete (DB connected)")
        else:
            logger.warning("Application startup complete (DB unavailable, degraded mode)")
    except Exception as e:
        # Should not happen due to degraded mode, but be safe
        logger.error(f"Startup DB error: {e}")
        


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("Application shutdown complete")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "database": "connected" if db.connected else "unavailable",
    }
    return status


@app.get("/api/health", tags=["Health"])
async def api_health_check():
    """Health check endpoint under /api prefix"""
    return await health_check()


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(hospital.router, prefix="/api")
app.include_router(patient.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# Import and include new routers
from app.routes import surge, capacity, referrals, search, wallet, alerts, advertisements, inventory, reviews, chat, notifications, appointments, medications, analytics, telemedicine, workflows, location
app.include_router(surge.router, prefix="/api")
app.include_router(capacity.router, prefix="/api")
app.include_router(referrals.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(wallet.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(advertisements.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(medications.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(telemedicine.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(location.router)


# Error handlers
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
