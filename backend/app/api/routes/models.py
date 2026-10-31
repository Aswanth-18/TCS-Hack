from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.entities import ModelRegistryItem
from app.schemas.dtos import ModelDTO, ModelUpdateDTO
from app.services.model_registry import ModelRegistryService

router = APIRouter(prefix="/models", tags=["Models"])

@router.get("", response_model=List[ModelDTO])
def list_models(db: Session = Depends(get_db)):
    """List all models in the registry."""
    models = db.query(ModelRegistryItem).all()
    if not models:
        models = ModelRegistryService.seed_default_models(db)
    return models

@router.post("", response_model=ModelDTO)
def create_model(model_dto: ModelDTO, db: Session = Depends(get_db)):
    """Register a new AI model in the registry."""
    existing = db.query(ModelRegistryItem).filter(ModelRegistryItem.model_id == model_dto.model_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Model '{model_dto.model_id}' is already registered.")

    new_model = ModelRegistryItem(**model_dto.model_dump(exclude={"id"}))
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return new_model

@router.patch("/{model_id}", response_model=ModelDTO)
def update_model(model_id: str, update_data: ModelUpdateDTO, db: Session = Depends(get_db)):
    """Update model settings (enabled, pricing, latency, health status)."""
    model = db.query(ModelRegistryItem).filter(ModelRegistryItem.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    for key, val in update_data.model_dump(exclude_unset=True).items():
        setattr(model, key, val)

    db.commit()
    db.refresh(model)
    return model

@router.delete("/{model_id}")
def delete_model(model_id: str, db: Session = Depends(get_db)):
    """Remove a model from the registry (or safely deactivate if referenced in audit history)."""
    model = db.query(ModelRegistryItem).filter(ModelRegistryItem.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    from app.models.entities import RequestAuditLog, ExecutionAttempt
    has_audit = db.query(RequestAuditLog).filter(RequestAuditLog.selected_model_id == model_id).first()
    has_attempts = db.query(ExecutionAttempt).filter(ExecutionAttempt.model_id == model_id).first()

    if has_audit or has_attempts:
        model.enabled = False
        db.commit()
        return {
            "status": "deactivated",
            "message": f"Model '{model_id}' is referenced in audit history. It has been deactivated to preserve audit integrity.",
            "model_id": model_id,
            "enabled": False
        }

    db.delete(model)
    db.commit()
    return {
        "status": "deleted",
        "message": f"Model '{model_id}' was removed from the registry.",
        "model_id": model_id
    }

