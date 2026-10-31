from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.models.entities import BenchmarkRun, BenchmarkItem
from app.services.benchmark_runner import BenchmarkRunner

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])

@router.get("/dataset")
def get_benchmark_dataset(limit: int = 50, db: Session = Depends(get_db)):
    """List representative benchmark tasks in the suite."""
    items = db.query(BenchmarkItem).limit(limit).all()
    if not items:
        BenchmarkRunner.seed_dataset(db)
        items = db.query(BenchmarkItem).limit(limit).all()
    return items

def serialize_run(r: BenchmarkRun) -> Dict[str, Any]:
    return {
        "id": r.id,
        "dataset_name": r.dataset_name,
        "strategy": r.strategy,
        "status": r.status,
        "total_items": r.total_items,
        "successful_items": r.successful_items,
        "failed_items": r.failed_items,
        "total_cost_usd": r.total_cost_usd,
        "cost_per_successful_outcome": r.cost_per_successful_outcome,
        "avg_latency_ms": r.avg_latency_ms,
        "avg_quality_score": r.avg_quality_score,
        "verification_success_rate": r.verification_success_rate,
        "fallback_rate": r.fallback_rate,
        "created_at": r.created_at.isoformat() if r.created_at else "",
        "details": r.details or []
    }

@router.post("/run")
def run_benchmark(
    limit: int = Query(15, ge=5, le=50),
    dataset_name: str = "Standard FinOps Suite",
    db: Session = Depends(get_db)
):
    """
    Module 8: Live Routing Arena.
    Executes all 4 strategies (Always Advanced, Cheapest Eligible, Rule-Based, AstraRoute)
    on the exact same workload and returns side-by-side performance metrics.
    """
    runs = BenchmarkRunner.run_benchmark_comparison(db, limit=limit, dataset_name=dataset_name)
    return [serialize_run(r) for r in runs]

@router.get("")
@router.get("/history")
def get_benchmark_history(db: Session = Depends(get_db)):
    """Get history of benchmark runs."""
    runs = db.query(BenchmarkRun).order_by(desc(BenchmarkRun.created_at)).limit(20).all()
    return [serialize_run(r) for r in runs]

@router.get("/export")
def export_benchmark_csv(db: Session = Depends(get_db)):
    """Export benchmark run results to CSV format."""
    runs = db.query(BenchmarkRun).order_by(desc(BenchmarkRun.created_at)).limit(8).all()
    if not runs:
        runs = BenchmarkRunner.run_benchmark_comparison(db, limit=10)

    csv_data = BenchmarkRunner.export_csv(runs)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=astraroute_benchmark_comparison.csv"}
    )

@router.get("/{run_id}")
def get_benchmark_run(run_id: str, db: Session = Depends(get_db)):
    """Get details of a specific benchmark run."""
    run = db.query(BenchmarkRun).filter(BenchmarkRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Benchmark run not found")
    return run

