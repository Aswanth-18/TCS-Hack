from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("")
def list_audit_events(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    task_type: Optional[str] = None,
    model_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Module 12: Query traceable audit records."""
    return AuditService.get_audit_logs(
        db=db,
        limit=limit,
        offset=offset,
        task_type=task_type,
        model_id=model_id,
        status=status
    )

@router.get("/{request_id}")
def get_audit_detail(request_id: str, db: Session = Depends(get_db)):
    """Retrieve complete audit trace and execution attempts for a single request."""
    item = AuditService.get_single_request(request_id, db)
    if not item:
        raise HTTPException(status_code=404, detail="Request trace not found")
    return item

