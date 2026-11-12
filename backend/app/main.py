import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User
from backend.app.utils.security import hash_password
from backend.app.routers import (
    auth_router,
    users_router,
    plants_router,
    lines_router,
    machines_router,
    shifts_router,
    products_router,
    downtime_router,
    po_router,
    events_router,
    counts_router,
    qc_router,
    oee_router,
    anomalies_router,
    reports_router,
    assistant_router
)

logger = logging.getLogger("factorypulse")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FactoryPulse – Smart Manufacturing Performance & OEE Monitoring Platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api/v1
api_v1 = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1)
app.include_router(users_router, prefix=api_v1)
app.include_router(plants_router, prefix=api_v1)
app.include_router(lines_router, prefix=api_v1)
app.include_router(machines_router, prefix=api_v1)
app.include_router(shifts_router, prefix=api_v1)
app.include_router(products_router, prefix=api_v1)
app.include_router(downtime_router, prefix=api_v1)
app.include_router(po_router, prefix=api_v1)
app.include_router(events_router, prefix=api_v1)
app.include_router(counts_router, prefix=api_v1)
app.include_router(qc_router, prefix=api_v1)
app.include_router(oee_router, prefix=api_v1)
app.include_router(anomalies_router, prefix=api_v1)
app.include_router(reports_router, prefix=api_v1)
app.include_router(assistant_router, prefix=api_v1)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema verified.")

    # Seed default admin user if no users exist
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.info("Seeding default administrator account (admin / admin123)...")
            new_admin = User(
                username="admin",
                email="admin@factorypulse.internal",
                full_name="System Administrator",
                role="ADMIN",
                is_active=True,
                password_hash=hash_password("admin123")
            )
            db.add(new_admin)
            db.commit()
            logger.info("Default administrator created successfully.")
    except Exception as e:
        logger.error(f"Error during startup user verification: {e}")
    finally:
        db.close()


# Mount frontend static directory if exists
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_frontend_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "FactoryPulse API running. Visit /docs for Swagger documentation."}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }
