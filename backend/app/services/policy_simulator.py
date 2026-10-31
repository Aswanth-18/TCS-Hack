from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.entities import RoutingPolicy, ModelRegistryItem, BenchmarkItem
from app.schemas.dtos import (
    PolicySimulateRequest, PolicySimulateResponse,
    RequestAnalysisRequest, TaskType
)
from app.services.request_analyzer import RequestAnalyzer
from app.services.eligibility_filter import EligibilityFilter
from app.services.router import IntelligentRouter
from app.services.cost_calculator import CostCalculator

class PolicySimulator:
    @classmethod
    def simulate(cls, req: PolicySimulateRequest, db: Session) -> PolicySimulateResponse:
        active_policy = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
        current_policy_dict = {
            "version": active_policy.version if active_policy else 1,
            "max_budget_per_request": active_policy.max_budget_per_request if active_policy else 0.05,
            "min_quality_threshold": active_policy.min_quality_threshold if active_policy else 0.70,
            "max_latency_ms": active_policy.max_latency_ms if active_policy else 4000,
            "weight_cost": active_policy.weight_cost if active_policy else 0.40,
            "weight_quality": active_policy.weight_quality if active_policy else 0.35,
            "weight_latency": active_policy.weight_latency if active_policy else 0.15,
            "weight_reliability": active_policy.weight_reliability if active_policy else 0.10
        }

        # Proposed virtual policy
        proposed_policy = RoutingPolicy(
            version=(active_policy.version + 1) if active_policy else 2,
            name="Proposed What-If Simulation Policy",
            max_budget_per_request=req.max_budget_per_request,
            min_quality_threshold=req.min_quality_threshold,
            max_latency_ms=req.max_latency_ms,
            weight_cost=req.weight_cost,
            weight_quality=req.weight_quality,
            weight_latency=req.weight_latency,
            weight_reliability=req.weight_reliability
        )

        all_models = db.query(ModelRegistryItem).all()
        if not all_models:
            from app.services.model_registry import ModelRegistryService
            all_models = ModelRegistryService.seed_default_models(db)

        # Apply disabled providers if requested
        if req.disabled_providers:
            disabled_set = set([p.lower() for p in req.disabled_providers])
            available_models = [m for m in all_models if m.provider.lower() not in disabled_set]
        else:
            available_models = all_models

        benchmark_sample = db.query(BenchmarkItem).limit(30).all()
        if not benchmark_sample:
            from app.services.benchmark_runner import BenchmarkRunner
            BenchmarkRunner.seed_dataset(db)
            benchmark_sample = db.query(BenchmarkItem).limit(30).all()

        current_total_spend = 0.0
        projected_spend = 0.0
        projected_latencies = []
        projected_qualities = []
        model_counts: Dict[str, int] = {}
        budget_violations = 0

        for item in benchmark_sample:
            analysis = RequestAnalyzer.analyze(RequestAnalysisRequest(
                prompt=item.prompt,
                task_type=TaskType(item.task_category)
            ))

            # 1. Current selection
            curr_eligible, _ = EligibilityFilter.filter_candidates(
                candidates=all_models,
                analysis=analysis,
                user_budget_max=current_policy_dict["max_budget_per_request"],
                user_latency_max=current_policy_dict["max_latency_ms"],
                user_min_quality=current_policy_dict["min_quality_threshold"]
            )
            if curr_eligible:
                curr_model, _, _, _ = IntelligentRouter.select_model(
                    strategy="astraroute_intelligent",
                    eligible_models=curr_eligible,
                    analysis=analysis,
                    policy=active_policy
                )
                curr_cost = CostCalculator.calculate_token_cost(
                    analysis.estimated_input_tokens,
                    analysis.estimated_output_tokens,
                    curr_model.input_cost_per_m,
                    curr_model.output_cost_per_m
                )
                current_total_spend += curr_cost

            # 2. Proposed selection
            prop_eligible, prop_rejected = EligibilityFilter.filter_candidates(
                candidates=available_models,
                analysis=analysis,
                user_budget_max=req.max_budget_per_request,
                user_latency_max=req.max_latency_ms,
                user_min_quality=req.min_quality_threshold
            )

            if not prop_eligible:
                budget_violations += 1
                continue

            prop_model, _, _, _ = IntelligentRouter.select_model(
                strategy="astraroute_intelligent",
                eligible_models=prop_eligible,
                analysis=analysis,
                policy=proposed_policy
            )

            p_cost = CostCalculator.calculate_token_cost(
                analysis.estimated_input_tokens,
                analysis.estimated_output_tokens,
                prop_model.input_cost_per_m,
                prop_model.output_cost_per_m
            )
            projected_spend += p_cost
            projected_latencies.append(prop_model.latency_p50_ms)
            projected_qualities.append(prop_model.benchmark_quality_score)
            model_counts[prop_model.model_id] = model_counts.get(prop_model.model_id, 0) + 1

        total_eval = len(benchmark_sample)
        total_routed = max(1, len(projected_qualities))
        
        # Calculate savings %
        savings_pct = 0.0
        if current_total_spend > 0:
            savings_pct = round(((current_total_spend - projected_spend) / current_total_spend) * 100, 2)

        avg_lat = round(sum(projected_latencies) / total_routed, 1) if projected_latencies else 0.0
        avg_q = round(sum(projected_qualities) / total_routed, 3) if projected_qualities else 0.0
        dist = {m: round((cnt / total_routed) * 100, 1) for m, cnt in model_counts.items()}
        violation_pct = round((budget_violations / max(1, total_eval)) * 100, 1)

        # Build trade-off analysis narrative
        warnings = []
        if violation_pct > 15:
            warnings.append(f"High rejection rate ({violation_pct}%): Proposed budget/quality constraints may be too stringent for complex tasks.")
        if req.weight_cost > 0.7:
            warnings.append("Cost weight > 70%: Quality on coding/reasoning tasks may degrade due to aggressive economy model bias.")
        if req.min_quality_threshold > 0.90:
            warnings.append("Quality threshold > 90%: Will force majority traffic to top-tier flagship models, reducing cost savings.")

        trade_off = (
            f"Applying this policy would shift {savings_pct:+.1f}% in inference expenditures. "
            f"Projected quality baseline is {avg_q * 100:.1f}% with an average latency of {avg_lat:.0f}ms. "
            f"Most prevalent model under this configuration is '{max(dist, key=dist.get) if dist else 'none'}' "
            f"handling {max(dist.values()) if dist else 0}% of workload."
        )

        return PolicySimulateResponse(
            current_policy=current_policy_dict,
            proposed_policy=req.model_dump(),
            projected_spend_usd=round(projected_spend, 6),
            projected_savings_pct=savings_pct,
            projected_quality_score=avg_q,
            projected_avg_latency_ms=avg_lat,
            projected_model_distribution=dist,
            projected_budget_violations_pct=violation_pct,
            trade_off_analysis=trade_off,
            warnings=warnings
        )

