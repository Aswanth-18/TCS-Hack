from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.models.entities import RoutingPolicy
from app.schemas.dtos import PolicySimulateRequest, PolicySimulateResponse
from app.services.policy_simulator import PolicySimulator

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("")
def get_current_policy(db: Session = Depends(get_db)):
    """Retrieve currently active routing policy."""
    policy = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
    if not policy:
        from app.services.model_registry import ModelRegistryService
        ModelRegistryService.seed_default_models(db)
        policy = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
    return policy

@router.post("/simulate", response_model=PolicySimulateResponse)
def simulate_policy(req: PolicySimulateRequest, db: Session = Depends(get_db)):
    """
    Module 9: What-If Policy Simulator.
    Simulates proposed policy adjustments without altering live policies.
    """
    return PolicySimulator.simulate(req, db)

@router.post("/apply")
def apply_policy(req: PolicySimulateRequest, db: Session = Depends(get_db)):
    """
    Applies proposed policy to live traffic after explicit user confirmation.
    """
    current = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
    new_version = (current.version + 1) if current else 2

    # Deactivate current
    if current:
        current.is_active = False

    new_policy = RoutingPolicy(
        version=new_version,
        name=f"Custom Policy v{new_version}",
        description="Policy applied by operator via What-If Simulator",
        is_active=True,
        max_budget_per_request=req.max_budget_per_request,
        min_quality_threshold=req.min_quality_threshold,
        max_latency_ms=req.max_latency_ms,
        weight_cost=req.weight_cost,
        weight_quality=req.weight_quality,
        weight_latency=req.weight_latency,
        weight_reliability=req.weight_reliability,
        applied_by="Operator Web Console"
    )
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)

    return {
        "status": "success",
        "message": f"Successfully activated policy version {new_version}.",
        "policy": new_policy
    }

@router.post("/rollback")
def rollback_policy(db: Session = Depends(get_db)):
    """
    Rolls back to the previous policy version if available.
    """
    current = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
    if not current:
        raise HTTPException(status_code=400, detail="No active policy found")

    # Find previous policy
    previous = db.query(RoutingPolicy).filter(
        RoutingPolicy.id != current.id
    ).order_by(desc(RoutingPolicy.created_at)).first()

    if not previous:
        return {"status": "warning", "message": "No previous policy version available for rollback"}

    current.is_active = False
    previous.is_active = True
    db.commit()
    db.refresh(previous)

    return {
        "status": "success",
        "message": f"Successfully rolled back to policy version {previous.version} ({previous.name}).",
        "active_policy": previous
    }
