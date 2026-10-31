from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.dtos import AdaptiveObservationDTO, AdaptiveRollbackRequest
from app.services.adaptation_service import AdaptationService

router = APIRouter(prefix="/adaptation", tags=["Adaptation"])

@router.get("/history", response_model=List[AdaptiveObservationDTO])
def get_adaptation_history(db: Session = Depends(get_db)):
    """Module 10: Get empirical model performance statistics and update history."""
    return AdaptationService.get_all_observations(db)

@router.post("/rollback")
def rollback_observation(req: AdaptiveRollbackRequest, db: Session = Depends(get_db)):
    """Roll back an empirical observation score to its previous state."""
    result = AdaptationService.rollback_observation(req.model_id, req.task_category, db)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

