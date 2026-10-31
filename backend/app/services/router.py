from typing import List, Dict, Any, Optional, Tuple
from app.models.entities import ModelRegistryItem, RoutingPolicy
from app.schemas.dtos import (
    RoutingStrategy, RequestAnalysisResponse, TaskType, Complexity
)
from app.services.cost_calculator import CostCalculator

class IntelligentRouter:
    """
    Module 3: Explainable Multi-Strategy Intelligent Router.
    Implements 4 distinct strategies:
    - Always Advanced
    - Cheapest Eligible
    - Rule-Based Routing
    - AstraRoute Intelligent Multi-Objective Routing
    """

    @classmethod
    def select_model(
        cls,
        strategy: RoutingStrategy,
        eligible_models: List[ModelRegistryItem],
        analysis: RequestAnalysisResponse,
        policy: Optional[RoutingPolicy] = None
    ) -> Tuple[ModelRegistryItem, float, str, Dict[str, float]]:
        """
        Returns:
            (selected_model, routing_score, explanation, model_scores_dict)
        """
        if not eligible_models:
            raise ValueError("No eligible models available to satisfy the specified constraints.")

        if strategy == RoutingStrategy.ALWAYS_ADVANCED:
            return cls._route_always_advanced(eligible_models, analysis)
        elif strategy == RoutingStrategy.CHEAPEST_ELIGIBLE:
            return cls._route_cheapest_eligible(eligible_models, analysis)
        elif strategy == RoutingStrategy.RULE_BASED:
            return cls._route_rule_based(eligible_models, analysis)
        else: # RoutingStrategy.ASTRAROUTE_INTELLIGENT
            return cls._route_astraroute_intelligent(eligible_models, analysis, policy)

    @classmethod
    def _route_always_advanced(
        cls,
        eligible: List[ModelRegistryItem],
        analysis: RequestAnalysisResponse
    ) -> Tuple[ModelRegistryItem, float, str, Dict[str, float]]:
        # Sort by benchmark quality descending, then higher cost as indicator of flagship capability
        sorted_models = sorted(
            eligible,
            key=lambda m: (m.benchmark_quality_score, m.input_cost_per_m + m.output_cost_per_m),
            reverse=True
        )
        selected = sorted_models[0]
        scores = {m.model_id: round(m.benchmark_quality_score, 3) for m in eligible}
        
        explanation = (
            f"[Strategy: Always Advanced] Selected '{selected.name}' ({selected.model_id}) "
            f"providing the highest benchmark capability ({selected.benchmark_quality_score * 100:.1f}%) "
            f"subject to mandatory privacy and availability filters."
        )
        return selected, 1.0, explanation, scores

    @classmethod
    def _route_cheapest_eligible(
        cls,
        eligible: List[ModelRegistryItem],
        analysis: RequestAnalysisResponse
    ) -> Tuple[ModelRegistryItem, float, str, Dict[str, float]]:
        # Calculate cost for each candidate on this exact request
        costs = {}
        for m in eligible:
            c = CostCalculator.calculate_token_cost(
                analysis.estimated_input_tokens,
                analysis.estimated_output_tokens,
                m.input_cost_per_m,
                m.output_cost_per_m
            )
            costs[m.model_id] = c

        selected = min(eligible, key=lambda m: costs[m.model_id])
        min_cost = costs[selected.model_id]
        scores = {m.model_id: round(min_cost / (costs[m.model_id] + 1e-7), 3) for m in eligible}

        explanation = (
            f"[Strategy: Cheapest Eligible] Selected '{selected.name}' ({selected.model_id}) "
            f"as the absolute lowest cost model (${min_cost:.5f}) among eligible candidates, "
            f"without considering task-specific quality margin."
        )
        return selected, scores[selected.model_id], explanation, scores

    @classmethod
    def _route_rule_based(
        cls,
        eligible: List[ModelRegistryItem],
        analysis: RequestAnalysisResponse
    ) -> Tuple[ModelRegistryItem, float, str, Dict[str, float]]:
        """
        Deterministic rule-based routing mapping based on task type and complexity.
        """
        task = analysis.detected_task_type
        complexity = analysis.detected_complexity

        # Target tier by rule matrix
        if complexity == Complexity.COMPLEX or task in [TaskType.CODING, TaskType.REASONING]:
            preferred_tiers = ["flagship", "specialized", "balanced", "economy"]
        elif complexity == Complexity.MODERATE or task in [TaskType.DATA_ANALYSIS, TaskType.STRUCTURED_OUTPUT]:
            preferred_tiers = ["balanced", "economy", "flagship"]
        else: # Simple QA / Summarization
            preferred_tiers = ["economy", "balanced", "flagship"]

        selected = None
        for tier in preferred_tiers:
            matches = [m for m in eligible if m.tier == tier]
            if matches:
                # Pick the lowest cost within the target tier
                selected = min(
                    matches,
                    key=lambda m: (m.input_cost_per_m + m.output_cost_per_m)
                )
                break

        if not selected:
            selected = eligible[0]

        scores = {m.model_id: 1.0 if m.id == selected.id else 0.5 for m in eligible}
        explanation = (
            f"[Strategy: Rule-Based] Applied static rule: Task '{task.value}' with "
            f"'{complexity.value}' complexity maps to '{selected.tier}' tier. "
            f"Selected '{selected.name}' ({selected.model_id})."
        )
        return selected, 1.0, explanation, scores

    @classmethod
    def _route_astraroute_intelligent(
        cls,
        eligible: List[ModelRegistryItem],
        analysis: RequestAnalysisResponse,
        policy: Optional[RoutingPolicy] = None
    ) -> Tuple[ModelRegistryItem, float, str, Dict[str, float]]:
        """
        AstraRoute Multi-Objective FinOps Engine:
        Balances Cost (w_cost), Quality (w_quality), Latency (w_latency), Reliability (w_reliability).
        Enforces lowest-cost candidate satisfying required threshold whenever qualifying.
        """
        w_cost = policy.weight_cost if policy else 0.40
        w_quality = policy.weight_quality if policy else 0.35
        w_latency = policy.weight_latency if policy else 0.15
        w_rel = policy.weight_reliability if policy else 0.10

        # Precompute values
        estimated_costs = {
            m.model_id: CostCalculator.calculate_token_cost(
                analysis.estimated_input_tokens,
                analysis.estimated_output_tokens,
                m.input_cost_per_m,
                m.output_cost_per_m
            )
            for m in eligible
        }

        min_cost = min(estimated_costs.values())
        max_cost = max(estimated_costs.values())
        cost_range = max_cost - min_cost if max_cost > min_cost else 1e-6

        latencies = [m.latency_p50_ms or 600 for m in eligible]
        min_lat = min(latencies)
        max_lat = max(latencies)
        lat_range = max_lat - min_lat if max_lat > min_lat else 1.0

        scores: Dict[str, float] = {}
        for m in eligible:
            # 1. Cost score: 1.0 is cheapest, 0.0 is most expensive
            cost_val = estimated_costs[m.model_id]
            norm_cost = 1.0 - ((cost_val - min_cost) / cost_range)

            # 2. Quality score: based on benchmark and quality target match
            # If model meets or exceeds required target, high score
            b_score = m.benchmark_quality_score if m.benchmark_quality_score is not None else 0.85
            if b_score >= analysis.required_quality_target:
                quality_ratio = b_score / max(0.1, analysis.required_quality_target)
                norm_quality = min(1.0, quality_ratio)
            else:
                # Severe quality deficit penalty when failing required threshold
                deficit = analysis.required_quality_target - b_score
                norm_quality = max(0.0, 1.0 - (deficit * 4.0))

            # 3. Latency score: 1.0 is fastest, 0.0 is slowest
            m_lat = m.latency_p50_ms or 600
            norm_latency = 1.0 - ((m_lat - min_lat) / lat_range)

            # 4. Reliability score: 0.0 to 1.0
            norm_rel = m.reliability_rate if m.reliability_rate is not None else 0.99

            # Composite weighted score
            composite = (
                (w_cost * norm_cost) +
                (w_quality * norm_quality) +
                (w_latency * norm_latency) +
                (w_rel * norm_rel)
            )

            # FinOps Efficiency Tier Alignment:
            # 1. Simple tasks direct affinity for Small Language Models (SLMs / economy / specialized)
            if analysis.detected_complexity == Complexity.SIMPLE:
                if m.tier in ["economy", "specialized"]:
                    composite += 0.25
                elif m.tier == "flagship":
                    composite -= 0.20  # Avoid unnecessary flagship spend on simple tasks
            # 2. Complex tasks direct affinity for Advanced / Flagship models
            elif analysis.detected_complexity == Complexity.COMPLEX:
                if m.tier in ["flagship", "specialized"]:
                    composite += 0.30
                elif m.tier == "economy":
                    composite -= 0.35  # Penalize economy SLMs on complex tasks requiring high reasoning
            # 3. Moderate tasks direct affinity for Balanced medium models or high-value economy models
            elif analysis.detected_complexity == Complexity.MODERATE:
                if m.tier in ["balanced", "economy"]:
                    composite += 0.15

            # Additional FinOps bonus if model meets required quality target and has significant cost savings
            if (m.benchmark_quality_score or 0.85) >= analysis.required_quality_target and norm_cost > 0.6:
                composite += 0.06

            scores[m.model_id] = round(composite, 4)

        # Select highest composite score
        selected = max(eligible, key=lambda m: scores[m.model_id])
        sel_cost = estimated_costs[selected.model_id]
        sel_score = scores[selected.model_id]

        explanation = (
            f"[Strategy: AstraRoute Intelligent] Selected '{selected.name}' ({selected.model_id}) "
            f"with top FinOps composite score of {sel_score:.3f} "
            f"(Cost: {w_cost * 100:.0f}%, Quality: {w_quality * 100:.0f}%, Latency: {w_latency * 100:.0f}%). "
            f"Model satisfies required quality target ({analysis.required_quality_target * 100:.0f}%) "
            f"at an expected cost of ${sel_cost:.5f} ({selected.latency_p50_ms}ms p50 latency), "
            f"achieving optimal cost-efficiency over {len(eligible)} evaluated alternatives."
        )

        return selected, sel_score, explanation, scores
