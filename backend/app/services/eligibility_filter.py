from typing import List, Tuple, Dict, Any, Optional
from app.models.entities import ModelRegistryItem
from app.schemas.dtos import (
    RejectionReason, SensitivityTier, Complexity, RequestAnalysisResponse
)
from app.services.cost_calculator import CostCalculator

class EligibilityFilter:
    """
    Module 2: Eligibility and Privacy Filter.
    Applies deterministic hard constraints to exclude ineligible candidates before ranking.
    Produces explicit, audited rejection reasons for every excluded candidate.
    """

    # Privacy Tier Compatibility Hierarchy
    PRIVACY_HIERARCHY = {
        SensitivityTier.RESTRICTED: ["local_only", "zero_data_retention"],
        SensitivityTier.CONFIDENTIAL: ["local_only", "zero_data_retention", "hipaa_eligible", "enterprise"],
        SensitivityTier.INTERNAL: ["local_only", "zero_data_retention", "hipaa_eligible", "enterprise", "standard"],
        SensitivityTier.PUBLIC: ["local_only", "zero_data_retention", "hipaa_eligible", "enterprise", "standard"]
    }

    @classmethod
    def filter_candidates(
        cls,
        candidates: List[ModelRegistryItem],
        analysis: RequestAnalysisResponse,
        user_budget_max: Optional[float] = None,
        user_latency_max: Optional[int] = None,
        user_min_quality: Optional[float] = None,
        allowed_providers: Optional[List[str]] = None
    ) -> Tuple[List[ModelRegistryItem], List[RejectionReason]]:
        
        eligible: List[ModelRegistryItem] = []
        rejected: List[RejectionReason] = []

        budget_limit = user_budget_max if user_budget_max is not None else analysis.budget_limit_usd
        latency_limit = user_latency_max if user_latency_max is not None else analysis.latency_limit_ms
        quality_target = user_min_quality if user_min_quality is not None else analysis.required_quality_target
        
        allowed_prov_set = set([p.lower() for p in allowed_providers]) if allowed_providers else None
        acceptable_privacy_tiers = cls.PRIVACY_HIERARCHY.get(analysis.sensitivity, ["standard"])

        for model in candidates:
            # 1. Enabled check
            if not model.enabled:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason="Model is administratively disabled in registry",
                    category="model_disabled"
                ))
                continue

            # 2. Provider Health check
            if not model.is_healthy:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason=f"Provider '{model.provider}' health check degraded or circuit breaker tripped",
                    category="provider_unavailable"
                ))
                continue

            # 3. Allowed Provider restriction
            if allowed_prov_set and model.provider.lower() not in allowed_prov_set:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason=f"Provider '{model.provider}' not in user-approved providers list",
                    category="provider_restricted"
                ))
                continue

            # 4. Privacy & Data Handling Enforcement
            if model.privacy_tier not in acceptable_privacy_tiers:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason=(
                        f"Violates privacy policy: request sensitivity is '{analysis.sensitivity.value}', "
                        f"but model '{model.model_id}' only offers '{model.privacy_tier}' tier."
                    ),
                    category="privacy_policy_violation"
                ))
                continue

            # 5. Required Capabilities
            missing_caps = [
                cap for cap in analysis.required_capabilities 
                if cap not in (model.capabilities or [])
            ]
            if missing_caps:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason=f"Missing mandatory capabilities: {', '.join(missing_caps)}",
                    category="unsupported_capability"
                ))
                continue

            # 6. Budget Feasibility
            estimated_cost = CostCalculator.calculate_token_cost(
                input_tokens=analysis.estimated_input_tokens,
                output_tokens=analysis.estimated_output_tokens,
                input_cost_per_m=model.input_cost_per_m,
                output_cost_per_m=model.output_cost_per_m
            )
            if budget_limit is not None and estimated_cost > budget_limit:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason=f"Estimated cost ${estimated_cost:.5f} exceeds request budget cap of ${budget_limit:.5f}",
                    category="budget_limit_exceeded"
                ))
                continue

            # 7. Latency Tolerance
            latency_val = model.latency_p50_ms if model.latency_p50_ms is not None else 600
            if latency_limit is not None and latency_val > latency_limit:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason=f"Expected latency {latency_val}ms exceeds maximum allowed threshold of {latency_limit}ms",
                    category="latency_exceeded"
                ))
                continue

            # 8. Minimum Quality Baseline
            # If model benchmark score is significantly lower than quality target (margin 0.08)
            benchmark_val = model.benchmark_quality_score if model.benchmark_quality_score is not None else 0.85
            if (benchmark_val + 0.08) < quality_target:
                rejected.append(RejectionReason(
                    model_id=model.model_id,
                    reason=(
                        f"Historical benchmark score ({benchmark_val:.2f}) "
                        f"does not satisfy minimum required quality ({quality_target:.2f})"
                    ),
                    category="insufficient_quality"
                ))
                continue

            # Passed all hard constraints
            eligible.append(model)

        return eligible, rejected
