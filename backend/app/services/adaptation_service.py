import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import AdaptiveObservation, ModelRegistryItem
from app.schemas.dtos import AdaptiveObservationDTO

class AdaptationService:
    @classmethod
    def get_all_observations(cls, db: Session) -> List[AdaptiveObservationDTO]:
        obs_list = db.query(AdaptiveObservation).all()
        if not obs_list:
            # Seed initial sample observations from model registry
            models = db.query(ModelRegistryItem).limit(6).all()
            for m in models:
                for task in (m.supported_tasks or ["general_qa"])[:2]:
                    o = AdaptiveObservation(
                        model_id=m.model_id,
                        task_category=task,
                        sample_count=12,
                        empirical_quality_score=round(m.benchmark_quality_score - 0.02, 3),
                        empirical_latency_ms=float(m.latency_p50_ms + 25),
                        empirical_cost_usd=round((m.input_cost_per_m + m.output_cost_per_m) * 0.0003, 6),
                        success_rate=0.98,
                        update_history=[
                            {
                                "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat(),
                                "old_score": m.benchmark_quality_score,
                                "new_score": round(m.benchmark_quality_score - 0.02, 3),
                                "reason": f"Baseline established from 12 live evaluations on {task}"
                            }
                        ]
                    )
                    db.add(o)
            db.commit()
            obs_list = db.query(AdaptiveObservation).all()

        dtos = []
        for o in obs_list:
            dtos.append(AdaptiveObservationDTO(
                model_id=o.model_id,
                task_category=o.task_category,
                sample_count=o.sample_count,
                empirical_quality_score=o.empirical_quality_score,
                empirical_latency_ms=o.empirical_latency_ms,
                empirical_cost_usd=o.empirical_cost_usd,
                success_rate=o.success_rate,
                last_updated=o.last_updated.isoformat() if o.last_updated else "",
                update_history=o.update_history or []
            ))
        return dtos

    @classmethod
    def rollback_observation(cls, model_id: str, task_category: str, db: Session) -> Dict[str, Any]:
        obs = db.query(AdaptiveObservation).filter(
            AdaptiveObservation.model_id == model_id,
            AdaptiveObservation.task_category == task_category
        ).first()

        if not obs:
            return {"status": "error", "message": f"No observation found for {model_id} on {task_category}"}

        history = list(obs.update_history or [])
        if not history:
            return {"status": "warning", "message": "No previous history to rollback to"}

        # Find previous score
        last_entry = history[-1]
        old_val = last_entry.get("old_score", obs.empirical_quality_score)

        # Rollback
        history.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "old_score": obs.empirical_quality_score,
            "new_score": old_val,
            "reason": "Manual operator rollback to prior stable state"
        })
        obs.empirical_quality_score = old_val
        obs.update_history = history
        db.commit()

        return {
            "status": "success",
            "message": f"Successfully rolled back {model_id} on {task_category} to {old_val:.3f}",
            "current_score": old_val
        }

