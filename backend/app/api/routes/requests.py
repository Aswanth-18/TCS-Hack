from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.schemas.dtos import (
    RequestAnalysisRequest, RequestAnalysisResponse,
    ExecuteRequestDTO, ExecuteResponseDTO
)
from app.services.request_analyzer import RequestAnalyzer
from app.services.execution_engine import ExecutionEngine
from app.services.audit_service import AuditService

router = APIRouter(prefix="/requests", tags=["Requests"])

@router.post("/analyze", response_model=RequestAnalysisResponse)
async def analyze_request(req: RequestAnalysisRequest):
    """
    Module 1: Request & Policy Analyzer.
    Analyzes prompt, classifies task type, evaluates complexity & sensitivity,
    and returns deterministic constraints.
    """
    try:
        return RequestAnalyzer.analyze(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/execute", response_model=ExecuteResponseDTO)
async def execute_request(req: ExecuteRequestDTO, db: Session = Depends(get_db)):
    """
    Autonomous Gateway Execution.
    Runs analysis -> filtering -> intelligent routing -> model API execution ->
    Quality Guardian verification -> bounded fallback recovery -> telemetry logging.
    """
    try:
        return await ExecutionEngine.process_request(req, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def list_requests(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    task_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List recent executed requests and their statuses."""
    return AuditService.get_audit_logs(db=db, limit=limit, offset=offset, task_type=task_type)

@router.get("/{request_id}")
def get_request_detail(request_id: str, db: Session = Depends(get_db)):
    """Retrieve full request detail and telemetry."""
    req = AuditService.get_single_request(request_id, db)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req

@router.get("/{request_id}/trace")
def get_request_trace(request_id: str, db: Session = Depends(get_db)):
    """Retrieve full execution audit trace with attempt breakdowns."""
    req = AuditService.get_single_request(request_id, db)
    if not req:
        raise HTTPException(status_code=404, detail="Request trace not found")
    return req
