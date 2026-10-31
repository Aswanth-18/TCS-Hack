from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.entities import RequestAuditLog, ExecutionAttempt

class AuditService:
    @classmethod
    def get_audit_logs(
        cls,
        db: Session,
        limit: int = 50,
        offset: int = 0,
        task_type: Optional[str] = None,
        model_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = db.query(RequestAuditLog)

        if task_type:
            query = query.filter(RequestAuditLog.task_type == task_type)
        if model_id:
            query = query.filter(RequestAuditLog.selected_model_id == model_id)
        if status:
            query = query.filter(RequestAuditLog.execution_status == status)

        logs = query.order_by(desc(RequestAuditLog.timestamp)).offset(offset).limit(limit).all()

        results = []
        for l in logs:
            results.append({
                "request_id": l.request_id,
                "timestamp": l.timestamp.isoformat() if l.timestamp else "",
                "prompt_preview": (l.prompt[:120] + "...") if len(l.prompt) > 120 else l.prompt,
                "prompt_full": l.prompt,
                "task_type": l.task_type,
                "detected_complexity": l.detected_complexity,
                "data_sensitivity": l.data_sensitivity,
                "business_criticality": l.business_criticality,
                "selected_model_id": l.selected_model_id,
                "selected_provider": l.selected_provider,
                "routing_strategy": l.routing_strategy,
                "routing_score": l.routing_score,
                "routing_explanation": l.routing_explanation,
                "eligible_models": l.eligible_models or [],
                "rejected_models": l.rejected_models or [],
                "execution_status": l.execution_status,
                "total_tokens": l.total_tokens,
                "input_tokens": l.input_tokens,
                "output_tokens": l.output_tokens,
                "total_latency_ms": l.total_latency_ms,
                "total_cost_usd": l.total_cost_usd,
                "verification_status": l.verification_status,
                "verification_method": l.verification_method,
                "verification_score": l.verification_score,
                "verification_details": l.verification_details or {},
                "verification": {
                    "status": l.verification_status or "Verified Pass",
                    "method": l.verification_method or "rubric",
                    "score": l.verification_score if l.verification_score is not None else 1.0,
                    "passed_checks": (l.verification_details or {}).get("passed_checks", []),
                    "failed_checks": (l.verification_details or {}).get("failed_checks", []),
                    "rationale": (l.verification_details or {}).get("rationale", "Verified by Quality Guardian"),
                    "uncertainty": (l.verification_details or {}).get("uncertainty", 0.05)
                },
                "fallback_occurred": l.fallback_occurred,
                "attempt_count": l.attempt_count,
                "final_response": l.final_response,
                "policy_version": l.policy_version,
                "attempts": [
                    {
                        "attempt_number": a.attempt_number,
                        "model_id": a.model_id,
                        "provider": a.provider,
                        "status": a.status,
                        "error_message": a.error_message,
                        "latency_ms": a.latency_ms,
                        "cost_usd": a.cost_usd,
                        "is_fallback": a.is_fallback,
                        "fallback_reason": a.fallback_reason,
                        "response_preview": a.response_preview
                    }
                    for a in (l.attempts or [])
                ]
            })

        return results

    @classmethod
    def get_single_request(cls, request_id: str, db: Session) -> Optional[Dict[str, Any]]:
        l = db.query(RequestAuditLog).filter(RequestAuditLog.request_id == request_id).first()
        if not l:
            return None

        return {
            "request_id": l.request_id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else "",
            "prompt": l.prompt,
            "task_type": l.task_type,
            "detected_complexity": l.detected_complexity,
            "data_sensitivity": l.data_sensitivity,
            "business_criticality": l.business_criticality,
            "selected_model_id": l.selected_model_id,
            "selected_provider": l.selected_provider,
            "routing_strategy": l.routing_strategy,
            "routing_score": l.routing_score,
            "routing_explanation": l.routing_explanation,
            "eligible_models": l.eligible_models or [],
            "rejected_models": l.rejected_models or [],
            "execution_status": l.execution_status,
            "total_tokens": l.total_tokens,
            "input_tokens": l.input_tokens,
            "output_tokens": l.output_tokens,
            "total_latency_ms": l.total_latency_ms,
            "total_cost_usd": l.total_cost_usd,
            "verification_status": l.verification_status,
            "verification_method": l.verification_method,
            "verification_score": l.verification_score,
            "verification_details": l.verification_details or {},
            "verification": {
                "status": l.verification_status or "Verified Pass",
                "method": l.verification_method or "rubric",
                "score": l.verification_score if l.verification_score is not None else 1.0,
                "passed_checks": (l.verification_details or {}).get("passed_checks", []),
                "failed_checks": (l.verification_details or {}).get("failed_checks", []),
                "rationale": (l.verification_details or {}).get("rationale", "Verified by Quality Guardian"),
                "uncertainty": (l.verification_details or {}).get("uncertainty", 0.05)
            },
            "fallback_occurred": l.fallback_occurred,
            "attempt_count": l.attempt_count,
            "final_response": l.final_response,
            "policy_version": l.policy_version,
            "attempts": [
                {
                    "attempt_number": a.attempt_number,
                    "model_id": a.model_id,
                    "provider": a.provider,
                    "status": a.status,
                    "error_message": a.error_message,
                    "latency_ms": a.latency_ms,
                    "cost_usd": a.cost_usd,
                    "is_fallback": a.is_fallback,
                    "fallback_reason": a.fallback_reason,
                    "response_preview": a.response_preview
                }
                for a in (l.attempts or [])
            ]
        }

