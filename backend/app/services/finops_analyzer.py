from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.entities import RequestAuditLog, ExecutionAttempt
from app.schemas.dtos import FinOpsSummaryDTO
from app.services.cost_calculator import CostCalculator

class FinOpsAnalyzer:
    @classmethod
    def get_summary(cls, db: Session) -> FinOpsSummaryDTO:
        total_requests = db.query(func.count(RequestAuditLog.id)).scalar() or 0

        if total_requests == 0:
            return FinOpsSummaryDTO(
                total_requests=0,
                verified_success_rate=0.0,
                total_spend_usd=0.0,
                cost_per_successful_outcome=None,
                average_latency_ms=0.0,
                total_tokens=0,
                fallback_rate=0.0,
                budget_utilization_pct=0.0,
                spend_by_provider={},
                spend_by_model={},
                spend_by_task={},
                strategy_comparison=[]
            )

        # Verified success count
        verified_count = db.query(func.count(RequestAuditLog.id)).filter(
            RequestAuditLog.verification_status.in_(["Verified Pass", "Partially Verified"])
        ).scalar() or 0

        # Total spend across all attempts
        total_spend = db.query(func.sum(RequestAuditLog.total_cost_usd)).scalar() or 0.0
        total_spend = round(total_spend, 6)

        # Average latency
        avg_lat = db.query(func.avg(RequestAuditLog.total_latency_ms)).scalar() or 0.0

        # Total tokens
        total_toks = db.query(func.sum(RequestAuditLog.total_tokens)).scalar() or 0

        # Fallback occurrences
        fallback_count = db.query(func.count(RequestAuditLog.id)).filter(
            RequestAuditLog.fallback_occurred == True
        ).scalar() or 0

        # Cost Per Successful Outcome
        cpso = CostCalculator.calculate_cost_per_successful_outcome(
            total_cost_all_attempts=total_spend,
            verified_success_count=verified_count
        )

        success_rate = round(float(verified_count) / float(total_requests), 4)
        fallback_rate = round(float(fallback_count) / float(total_requests), 4)

        # Spend by Provider
        provider_rows = db.query(
            RequestAuditLog.selected_provider,
            func.sum(RequestAuditLog.total_cost_usd)
        ).group_by(RequestAuditLog.selected_provider).all()
        spend_by_provider = {p or "unknown": round(float(c or 0.0), 6) for p, c in provider_rows}

        # Spend by Model
        model_rows = db.query(
            RequestAuditLog.selected_model_id,
            func.sum(RequestAuditLog.total_cost_usd)
        ).group_by(RequestAuditLog.selected_model_id).all()
        spend_by_model = {m or "unknown": round(float(c or 0.0), 6) for m, c in model_rows}

        # Spend by Task
        task_rows = db.query(
            RequestAuditLog.task_type,
            func.sum(RequestAuditLog.total_cost_usd)
        ).group_by(RequestAuditLog.task_type).all()
        spend_by_task = {t or "unknown": round(float(c or 0.0), 6) for t, c in task_rows}

        # Strategy Comparison
        strat_rows = db.query(
            RequestAuditLog.routing_strategy,
            func.count(RequestAuditLog.id),
            func.sum(RequestAuditLog.total_cost_usd),
            func.avg(RequestAuditLog.total_latency_ms),
            func.sum(case((RequestAuditLog.verification_status.in_(["Verified Pass", "Partially Verified"]), 1), else_=0))
        ).group_by(RequestAuditLog.routing_strategy).all()

        strategy_comparison = []
        for strat, count, spend, lat, succ in strat_rows:
            strat_spend = round(float(spend or 0.0), 6)
            strat_succ = int(succ or 0)
            strat_cpso = CostCalculator.calculate_cost_per_successful_outcome(strat_spend, strat_succ)
            strategy_comparison.append({
                "strategy": strat,
                "request_count": count,
                "total_spend_usd": strat_spend,
                "avg_latency_ms": round(float(lat or 0.0), 1),
                "verified_successes": strat_succ,
                "success_rate": round(strat_succ / max(1, count), 4),
                "cost_per_successful_outcome": strat_cpso
            })

        return FinOpsSummaryDTO(
            total_requests=total_requests,
            verified_success_rate=success_rate,
            total_spend_usd=total_spend,
            cost_per_successful_outcome=cpso,
            average_latency_ms=round(float(avg_lat), 1),
            total_tokens=total_toks,
            fallback_rate=fallback_rate,
            budget_utilization_pct=min(100.0, round((total_spend / max(1.0, total_requests * 0.05)) * 100, 1)),
            spend_by_provider=spend_by_provider,
            spend_by_model=spend_by_model,
            spend_by_task=spend_by_task,
            strategy_comparison=strategy_comparison
        )

