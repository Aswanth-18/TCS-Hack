from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.services.audit_service import AuditService

router = APIRouter(prefix="/routing", tags=["Routing"])

@router.get("/history")
def get_routing_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    task_type: Optional[str] = None,
    model_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve full routing decisions history with scoring explanations & traces."""
    return AuditService.get_audit_logs(
        db=db,
        limit=limit,
        offset=offset,
        task_type=task_type,
        model_id=model_id,
        status=status
    )

