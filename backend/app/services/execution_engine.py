import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.entities import (
    ModelRegistryItem, RoutingPolicy, RequestAuditLog, ExecutionAttempt, AdaptiveObservation
)
from app.schemas.dtos import (
    ExecuteRequestDTO, ExecuteResponseDTO, AttemptDTO,
    RequestAnalysisRequest, RequestAnalysisResponse, RoutingStrategy,
    VerificationStatus, RejectionReason
)
from app.services.request_analyzer import RequestAnalyzer
from app.services.eligibility_filter import EligibilityFilter
from app.services.router import IntelligentRouter
from app.services.provider_adapters.factory import ProviderAdapterFactory
from app.services.quality_guardian import QualityGuardian
from app.services.cost_calculator import CostCalculator

class ExecutionEngine:
    """
    Core Gateway Execution & Bounded Recovery Engine.
    Executes request -> verifies result -> triggers bounded fallback on failure ->
    tracks total multi-attempt telemetry & persists audit records.
    """

    @classmethod
    async def process_request(
        cls,
        req: ExecuteRequestDTO,
        db: Session
    ) -> ExecuteResponseDTO:
        request_id = str(uuid.uuid4())
        timestamp_now = datetime.datetime.now(datetime.timezone.utc)

        # Step 1: Analyze Request & Policies
        analysis_input = RequestAnalysisRequest(
            prompt=req.prompt,
            task_type=req.task_type,
            max_budget=req.max_budget,
            min_quality=req.min_quality,
            max_latency=req.max_latency,
            sensitivity=req.sensitivity,
            criticality=req.criticality,
            allowed_providers=req.allowed_providers
        )
        analysis = RequestAnalyzer.analyze(analysis_input)

        # Step 2: Fetch Active Models from DB Registry
        all_models = db.query(ModelRegistryItem).all()
        if not all_models:
            # Seed default models if table is empty
            from app.services.model_registry import ModelRegistryService
            all_models = ModelRegistryService.seed_default_models(db)

        # Step 3: Fetch Active Policy
        active_policy = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
        strategy = req.strategy or (
            RoutingStrategy(active_policy.default_strategy) if active_policy else RoutingStrategy.ASTRAROUTE_INTELLIGENT
        )
        max_retries = active_policy.max_retries if active_policy else 2
        request_budget_cap = req.max_budget or (active_policy.max_budget_per_request if active_policy else 0.05)

        # Step 4: Eligibility & Privacy Filtering
        eligible_models, rejected_reasons = EligibilityFilter.filter_candidates(
            candidates=all_models,
            analysis=analysis,
            user_budget_max=req.max_budget,
            user_latency_max=req.max_latency,
            user_min_quality=req.min_quality,
            allowed_providers=req.allowed_providers
        )

        if not eligible_models:
            # Honest rejection if no model qualifies
            audit_log = RequestAuditLog(
                request_id=request_id,
                timestamp=timestamp_now,
                prompt=req.prompt,
                task_type=analysis.detected_task_type.value,
                detected_complexity=analysis.detected_complexity.value,
                estimated_tokens=analysis.estimated_total_tokens,
                data_sensitivity=analysis.sensitivity.value,
                business_criticality=analysis.criticality.value,
                selected_model_id="none",
                selected_provider="none",
                routing_strategy=strategy.value,
                routing_score=0.0,
                routing_explanation="Zero models qualified after hard privacy, capability, or budget filters.",
                eligible_models=[],
                rejected_models=[r.model_dump() for r in rejected_reasons],
                execution_status="rejected_no_eligible_models",
                total_tokens=0,
                total_latency_ms=0,
                total_cost_usd=0.0,
                verification_status="Verification Unavailable",
                verification_method="none",
                verification_score=0.0,
                final_response="Request could not be routed. No eligible models satisfied your hard privacy, budget, or capability constraints."
            )
            db.add(audit_log)
            db.commit()

            return ExecuteResponseDTO(
                request_id=request_id,
                timestamp=timestamp_now.isoformat(),
                prompt=req.prompt,
                task_type=analysis.detected_task_type.value,
                detected_complexity=analysis.detected_complexity.value,
                selected_model_id="none",
                selected_provider="none",
                routing_strategy=strategy.value,
                routing_score=0.0,
                routing_explanation="No eligible model satisfied constraints.",
                eligible_models=[],
                rejected_models=rejected_reasons,
                execution_status="rejected_no_eligible_models",
                total_tokens=0,
                input_tokens=0,
                output_tokens=0,
                total_latency_ms=0,
                total_cost_usd=0.0,
                is_simulated=True,
                final_response="Request could not be routed. No eligible models satisfied your hard constraints.",
                verification=QualityGuardian.verify(analysis.detected_task_type, ""),
                fallback_occurred=False,
                attempt_count=0,
                attempts=[],
                policy_version=active_policy.version if active_policy else 1
            )

        # Step 5: Initial Model Selection
        selected_model, routing_score, explanation, model_scores = IntelligentRouter.select_model(
            strategy=strategy,
            eligible_models=eligible_models,
            analysis=analysis,
            policy=active_policy
        )

        # Execution & Recovery Loop
        attempts: List[AttemptDTO] = []
        current_candidate = selected_model
        remaining_candidates = [m for m in eligible_models if m.model_id != current_candidate.model_id]
        
        total_cost = 0.0
        total_latency = 0
        total_in_toks = 0
        total_out_toks = 0
        fallback_occurred = False
        final_response_text = ""
        verification_report = None
        execution_success = False

        attempt_idx = 0
        while attempt_idx <= max_retries and current_candidate:
            attempt_idx += 1
            is_fallback_attempt = (attempt_idx > 1)
            fallback_reason_text = None
            if is_fallback_attempt:
                fallback_occurred = True
                fallback_reason_text = "Prior attempt timed out or failed verification; escalated to next eligible candidate."

            # Force failure on first attempt only if user asked to simulate failure for testing fallback
            force_fail = bool(req.simulate_failure_attempt and attempt_idx == 1)

            # Get Provider Adapter
            adapter = ProviderAdapterFactory.get_adapter(current_candidate.provider)
            res = await adapter.execute(
                prompt=req.prompt,
                model_id=current_candidate.model_id,
                simulate_failure=force_fail
            )

            # Calculate token cost for this specific attempt
            attempt_cost = CostCalculator.calculate_token_cost(
                input_tokens=res.input_tokens,
                output_tokens=res.output_tokens,
                input_cost_per_m=current_candidate.input_cost_per_m,
                output_cost_per_m=current_candidate.output_cost_per_m
            )

            total_cost += attempt_cost
            total_latency += res.latency_ms
            total_in_toks += res.input_tokens
            total_out_toks += res.output_tokens

            # Step 7: Verify result
            v_report = QualityGuardian.verify(
                task_type=analysis.detected_task_type,
                response_text=res.response_text
            )

            # Check if this attempt succeeded
            attempt_passed = (res.status == "success" and v_report.status in [VerificationStatus.VERIFIED_PASS, VerificationStatus.PARTIALLY_VERIFIED])

            attempt_dto = AttemptDTO(
                attempt_number=attempt_idx,
                model_id=current_candidate.model_id,
                provider=current_candidate.provider,
                status=res.status if res.status != "success" else ("success" if attempt_passed else "verification_failed"),
                error_message=res.error_message or (None if attempt_passed else "Quality Guardian verification failed"),
                latency_ms=res.latency_ms,
                input_tokens=res.input_tokens,
                output_tokens=res.output_tokens,
                cost_usd=attempt_cost,
                is_fallback=is_fallback_attempt,
                fallback_reason=fallback_reason_text,
                response_preview=res.response_text[:120] if res.response_text else ""
            )
            attempts.append(attempt_dto)

            if attempt_passed:
                execution_success = True
                final_response_text = res.response_text
                verification_report = v_report
                break
            else:
                # Check remaining budget before fallback
                if total_cost >= request_budget_cap:
                    break
                # Escalate to next candidate
                if remaining_candidates:
                    # Sort remaining candidates by quality descending
                    remaining_candidates.sort(key=lambda m: m.benchmark_quality_score, reverse=True)
                    current_candidate = remaining_candidates.pop(0)
                else:
                    break

        if not verification_report:
            verification_report = QualityGuardian.verify(
                task_type=analysis.detected_task_type,
                response_text=final_response_text
            )

        final_status = "success" if execution_success else ("failed" if not attempts else attempts[-1].status)

        # Step 8: Persist in Database (RequestAuditLog & ExecutionAttempt)
        audit_log = RequestAuditLog(
            request_id=request_id,
            timestamp=timestamp_now,
            prompt=req.prompt,
            task_type=analysis.detected_task_type.value,
            detected_complexity=analysis.detected_complexity.value,
            estimated_tokens=analysis.estimated_total_tokens,
            data_sensitivity=analysis.sensitivity.value,
            business_criticality=analysis.criticality.value,
            user_budget_max=req.max_budget,
            user_quality_min=req.min_quality,
            user_latency_max=req.max_latency,
            selected_model_id=current_candidate.model_id if current_candidate else selected_model.model_id,
            selected_provider=current_candidate.provider if current_candidate else selected_model.provider,
            routing_strategy=strategy.value,
            routing_score=routing_score,
            routing_explanation=explanation,
            eligible_models=[m.model_id for m in eligible_models],
            rejected_models=[r.model_dump() for r in rejected_reasons],
            execution_status=final_status,
            total_tokens=total_in_toks + total_out_toks,
            input_tokens=total_in_toks,
            output_tokens=total_out_toks,
            total_latency_ms=total_latency,
            total_cost_usd=round(total_cost, 6),
            is_simulated=any(att.is_fallback for att in attempts) or True, # Simulator or live
            verification_status=verification_report.status.value,
            verification_method=verification_report.method,
            verification_score=verification_report.score,
            verification_details=verification_report.model_dump(),
            fallback_occurred=fallback_occurred,
            attempt_count=len(attempts),
            final_response=final_response_text or (attempts[-1].error_message if attempts else "Execution failed"),
            policy_version=active_policy.version if active_policy else 1
        )
        db.add(audit_log)

        for att in attempts:
            exec_att = ExecutionAttempt(
                request_id=request_id,
                attempt_number=att.attempt_number,
                model_id=att.model_id,
                provider=att.provider,
                status=att.status,
                error_message=att.error_message,
                latency_ms=att.latency_ms,
                input_tokens=att.input_tokens,
                output_tokens=att.output_tokens,
                cost_usd=att.cost_usd,
                is_fallback=att.is_fallback,
                fallback_reason=att.fallback_reason,
                response_preview=att.response_preview
            )
            db.add(exec_att)

        # Step 9: Update Adaptive Observations (Feedback loop)
        if current_candidate:
            obs = db.query(AdaptiveObservation).filter(
                AdaptiveObservation.model_id == current_candidate.model_id,
                AdaptiveObservation.task_category == analysis.detected_task_type.value
            ).first()

            if not obs:
                obs = AdaptiveObservation(
                    model_id=current_candidate.model_id,
                    task_category=analysis.detected_task_type.value,
                    sample_count=1,
                    empirical_quality_score=verification_report.score,
                    empirical_latency_ms=float(total_latency),
                    empirical_cost_usd=float(total_cost),
                    success_rate=1.0 if execution_success else 0.0,
                    update_history=[{
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "old_score": current_candidate.benchmark_quality_score,
                        "new_score": verification_report.score,
                        "reason": f"Initial observation for {analysis.detected_task_type.value}"
                    }]
                )
                db.add(obs)
            else:
                # Exponential moving average smoothing (alpha = 0.2)
                alpha = 0.2
                obs.sample_count += 1
                old_q = obs.empirical_quality_score
                new_q = (alpha * verification_report.score) + ((1.0 - alpha) * old_q)
                obs.empirical_quality_score = round(new_q, 4)
                obs.empirical_latency_ms = round((alpha * total_latency) + ((1.0 - alpha) * obs.empirical_latency_ms), 1)
                obs.empirical_cost_usd = round((alpha * total_cost) + ((1.0 - alpha) * obs.empirical_cost_usd), 6)
                history = list(obs.update_history or [])
                history.append({
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "old_score": old_q,
                    "new_score": obs.empirical_quality_score,
                    "reason": f"Observed verification score {verification_report.score:.2f} (sample #{obs.sample_count})"
                })
                obs.update_history = history[-10:] # Keep last 10 entries

        db.commit()

        return ExecuteResponseDTO(
            request_id=request_id,
            timestamp=timestamp_now.isoformat(),
            prompt=req.prompt,
            task_type=analysis.detected_task_type.value,
            detected_complexity=analysis.detected_complexity.value,
            selected_model_id=current_candidate.model_id if current_candidate else selected_model.model_id,
            selected_provider=current_candidate.provider if current_candidate else selected_model.provider,
            routing_strategy=strategy.value,
            routing_score=routing_score,
            routing_explanation=explanation,
            eligible_models=[m.model_id for m in eligible_models],
            rejected_models=rejected_reasons,
            execution_status=final_status,
            total_tokens=total_in_toks + total_out_toks,
            input_tokens=total_in_toks,
            output_tokens=total_out_toks,
            total_latency_ms=total_latency,
            total_cost_usd=round(total_cost, 6),
            is_simulated=True,
            final_response=final_response_text or (attempts[-1].error_message if attempts else "Execution failed"),
            verification=verification_report,
            fallback_occurred=fallback_occurred,
            attempt_count=len(attempts),
            attempts=attempts,
            policy_version=active_policy.version if active_policy else 1
        )

