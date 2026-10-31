from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from app.core.config import settings
from app.core.database import get_db
from app.models.entities import RoutingPolicy, ModelRegistryItem

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(response: Response, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    System Health Diagnostic.
    Truthfully reports database connectivity, provider status, and operating mode.
    Never crashes with 500 when dependencies are degraded.
    """
    db_ok = False
    models_count = 0
    active_policy_info = {"version": 1, "strategy": "astraroute_intelligent"}

    try:
        db.execute(text("SELECT 1"))
        db_ok = True
        
        # Safely query models and policy
        policy = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
        if policy:
            active_policy_info = {
                "version": policy.version,
                "strategy": policy.default_strategy
            }
        models_count = db.query(ModelRegistryItem).count()
    except Exception:
        db_ok = False

    provider_status = settings.get_provider_status()
    has_live = settings.has_any_live_provider()

    system_status = "healthy" if db_ok else "degraded"

    return {
        "status": system_status,
        "liveness": True,
        "readiness": db_ok,
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "Live Provider Mode" if has_live else "High-Fidelity Simulator Mode",
        "has_live_providers": has_live,
        "providers": provider_status,
        "database": {
            "connected": db_ok,
            "engine": "PostgreSQL / Supabase" if "postgres" in settings.DATABASE_URL else "SQLite (Local Dev)",
            "models_registered": models_count
        },
        "active_policy": active_policy_info
    }

@router.get("/live")
def liveness():
    """Liveness probe: verifies process is running."""
    return {"status": "alive", "timestamp_utc": settings.APP_VERSION}

@router.get("/ready")
def readiness(response: Response, db: Session = Depends(get_db)):
    """Readiness probe: verifies gateway is ready to accept traffic."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "reason": "Database connection unavailable"}

    return {"status": "ready", "database_connected": True}
