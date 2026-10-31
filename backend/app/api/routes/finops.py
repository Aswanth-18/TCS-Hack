from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.schemas.dtos import FinOpsSummaryDTO
from app.services.finops_analyzer import FinOpsAnalyzer
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/finops", tags=["FinOps"])

@router.get("/summary", response_model=FinOpsSummaryDTO)
def get_finops_summary(db: Session = Depends(get_db)):
    """Module 7: Aggregate FinOps KPI summary, including Cost Per Successful Outcome."""
    return FinOpsAnalyzer.get_summary(db)

@router.get("/recommendations")
def get_recommendations(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Module 11: Get autonomous FinOps optimization recommendations."""
    return RecommendationService.get_recommendations(db, status=status)

@router.post("/recommendations/{rec_id}/apply")
def apply_recommendation(rec_id: str, db: Session = Depends(get_db)):
    """Apply an approved FinOps recommendation to active routing policy."""
    result = RecommendationService.apply_recommendation(rec_id, db)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

@router.post("/recommendations/{rec_id}/dismiss")
def dismiss_recommendation(rec_id: str, db: Session = Depends(get_db)):
    """Dismiss a recommendation."""
    result = RecommendationService.dismiss_recommendation(rec_id, db)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

