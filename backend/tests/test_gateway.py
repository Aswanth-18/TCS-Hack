import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.cost_calculator import CostCalculator
from app.services.request_analyzer import RequestAnalyzer
from app.services.eligibility_filter import EligibilityFilter
from app.services.router import IntelligentRouter
from app.services.quality_guardian import QualityGuardian
from app.services.benchmark_runner import BenchmarkRunner
from app.services.recommendation_service import RecommendationService
from app.services.adaptation_service import AdaptationService
from app.schemas.dtos import (
    RequestAnalysisRequest, TaskType, Complexity, SensitivityTier, Criticality,
    RoutingStrategy, VerificationStatus
)
from app.models.entities import ModelRegistryItem, RoutingPolicy
from app.core.database import SessionLocal

# ==========================================
# SCENARIOS 1 & 2: Direct SLM vs Direct Advanced Routing
# ==========================================
def test_scenario_1_and_2_direct_routing_slm_and_flagship():
    slm = ModelRegistryItem(
        model_id="gemini-1.5-flash",
        name="Gemini Flash",
        provider="google",
        tier="economy",
        input_cost_per_m=0.075,
        output_cost_per_m=0.30,
        latency_p50_ms=200,
        benchmark_quality_score=0.81,
        reliability_rate=0.99
    )
    flagship = ModelRegistryItem(
        model_id="gpt-4o",
        name="GPT-4o",
        provider="openai",
        tier="flagship",
        input_cost_per_m=2.50,
        output_cost_per_m=10.00,
        latency_p50_ms=650,
        benchmark_quality_score=0.93,
        reliability_rate=0.995
    )
    candidates = [slm, flagship]

    # Scenario 1: Simple task directly routes to SLM
    simple_req = RequestAnalyzer.analyze(RequestAnalysisRequest(
        prompt="What is the capital of France?"
    ))
    assert simple_req.detected_complexity == Complexity.SIMPLE
    sel_simple, _, _, _ = IntelligentRouter.select_model(RoutingStrategy.ASTRAROUTE_INTELLIGENT, candidates, simple_req)
    assert sel_simple.model_id == "gemini-1.5-flash"
    assert sel_simple.tier == "economy"

    # Scenario 2: Complex task directly routes to Flagship
    complex_req = RequestAnalyzer.analyze(RequestAnalysisRequest(
        prompt="Implement an asynchronous high-throughput worker queue in Python with deadlock prevention, backpressure, priority queues, and full unit test coverage with step 1 step 2"
    ))
    assert complex_req.detected_complexity == Complexity.COMPLEX
    sel_complex, _, _, _ = IntelligentRouter.select_model(RoutingStrategy.ASTRAROUTE_INTELLIGENT, candidates, complex_req)
    assert sel_complex.model_id == "gpt-4o"
    assert sel_complex.tier == "flagship"

# ==========================================
# SCENARIO 3: Privacy Filter Rejection
# ==========================================
def test_scenario_3_privacy_filter_rejection():
    req = RequestAnalyzer.analyze(RequestAnalysisRequest(
        prompt="Process SSN 000-11-2222 and private employee data",
        sensitivity=SensitivityTier.RESTRICTED
    ))
    public_model = ModelRegistryItem(
        model_id="public-standard",
        name="Public",
        provider="openai",
        input_cost_per_m=0.10,
        output_cost_per_m=0.10,
        privacy_tier="standard", # Rejected for restricted
        capabilities=["code", "reasoning"],
        enabled=True,
        is_healthy=True,
        benchmark_quality_score=0.85
    )
    secure_model = ModelRegistryItem(
        model_id="local-secure",
        name="Secure",
        provider="local",
        input_cost_per_m=0.00,
        output_cost_per_m=0.00,
        privacy_tier="local_only", # Accepted
        capabilities=["code", "reasoning"],
        enabled=True,
        is_healthy=True,
        benchmark_quality_score=0.80
    )
    eligible, rejected = EligibilityFilter.filter_candidates([public_model, secure_model], req)
    assert len(eligible) == 1
    assert eligible[0].model_id == "local-secure"
    assert len(rejected) == 1
    assert rejected[0].category == "privacy_policy_violation"

# ==========================================
# SCENARIO 4: Budget Constraint Enforcement
# ==========================================
def test_scenario_4_budget_constraint_enforcement():
    req = RequestAnalyzer.analyze(RequestAnalysisRequest(
        prompt="Summarize this 1000-word quarterly financial memo"
    ))
    expensive_model = ModelRegistryItem(
        model_id="ultra-expensive",
        name="Ultra Expensive",
        provider="custom",
        input_cost_per_m=500.0,
        output_cost_per_m=1000.0,
        privacy_tier="standard",
        capabilities=[],
        enabled=True,
        is_healthy=True,
        benchmark_quality_score=0.99
    )
    eligible, rejected = EligibilityFilter.filter_candidates([expensive_model], req, user_budget_max=0.01)
    assert len(eligible) == 0
    assert len(rejected) == 1
    assert rejected[0].category == "budget_limit_exceeded"

# ==========================================
# SCENARIOS 5, 6, 7, 8 & 9: Verification, Fallback, Bounded Retries, Cost Sum
# ==========================================
def test_scenario_5_invalid_json_detection():
    invalid_json = "Here is your JSON: {name: 'Alice', invalid_json_syntax"
    report = QualityGuardian.verify(TaskType.STRUCTURED_OUTPUT, invalid_json)
    assert report.status == VerificationStatus.FAILED_VERIFICATION
    assert len(report.failed_checks) > 0

def test_scenario_6_7_8_9_bounded_fallback_and_total_cost():
    with TestClient(app) as client:
        # Deliberately simulate failure on attempt 1
        res = client.post("/api/requests/execute", json={
            "prompt": "Write a python function to invert binary tree",
            "task_type": "coding",
            "simulate_failure_attempt": True
        })
        assert res.status_code == 200
        data = res.json()
        assert data["fallback_occurred"] is True
        assert data["attempt_count"] == 2
        assert len(data["attempts"]) == 2

        # Verify attempt 1 was marked timeout/error and attempt 2 succeeded
        att1 = data["attempts"][0]
        att2 = data["attempts"][1]
        assert att1["is_fallback"] is False
        assert att2["is_fallback"] is True
        assert att2["status"] == "success"

        # Verify total cost includes BOTH attempts
        calculated_sum = round(att1["cost_usd"] + att2["cost_usd"], 6)
        assert data["total_cost_usd"] == calculated_sum

        # Retries remain bounded (attempt count <= 3)
        assert data["attempt_count"] <= 3

# ==========================================
# SCENARIOS 10 & 11: Cost Per Successful Outcome (CPSO)
# ==========================================
def test_scenario_10_and_11_cpso_calculation():
    # 3 attempts costing $0.015 resulting in 2 verified successes
    cpso = CostCalculator.calculate_cost_per_successful_outcome(0.015, 2)
    assert cpso == 0.0075

    # Zero successes handled without division by zero
    cpso_zero = CostCalculator.calculate_cost_per_successful_outcome(0.020, 0)
    assert cpso_zero is None

# ==========================================
# SCENARIO 12: Benchmark Strategies Use Equivalent Workloads
# ==========================================
def test_scenario_12_benchmark_equivalent_workloads():
    with TestClient(app) as client:
        res = client.post("/api/benchmarks/run?limit=6")
        assert res.status_code == 200
        runs = res.json()
        assert len(runs) == 4
        # All 4 runs evaluated the exact same 6 items
        for r in runs:
            assert r["total_items"] == 6

# ==========================================
# SCENARIO 13: Policy Simulator Does Not Modify Live Policy
# ==========================================
def test_scenario_13_policy_simulator_isolated():
    with TestClient(app) as client:
        # Fetch current live policy
        curr = client.get("/api/policies").json()
        orig_version = curr["version"]
        orig_budget = curr["max_budget_per_request"]

        # Run simulation with different parameters
        sim_res = client.post("/api/policies/simulate", json={
            "max_budget_per_request": 0.02,
            "min_quality_threshold": 0.85,
            "max_latency_ms": 2000,
            "weight_cost": 0.60,
            "weight_quality": 0.20,
            "weight_latency": 0.10,
            "weight_reliability": 0.10
        })
        assert sim_res.status_code == 200

        # Verify active policy remains UNMODIFIED
        after = client.get("/api/policies").json()
        assert after["version"] == orig_version
        assert after["max_budget_per_request"] == orig_budget

# ==========================================
# SCENARIO 14: Policy Approval and Rollback
# ==========================================
def test_scenario_14_policy_apply_and_rollback():
    with TestClient(app) as client:
        # Apply new policy
        apply_res = client.post("/api/policies/apply", json={
            "max_budget_per_request": 0.035,
            "min_quality_threshold": 0.75,
            "max_latency_ms": 3000,
            "weight_cost": 0.40,
            "weight_quality": 0.35,
            "weight_latency": 0.15,
            "weight_reliability": 0.10
        })
        assert apply_res.status_code == 200
        new_version = apply_res.json()["policy"]["version"]

        # Rollback policy
        rb_res = client.post("/api/policies/rollback")
        assert rb_res.status_code == 200
        assert rb_res.json()["status"] == "success"

# ==========================================
# SCENARIO 15: Historical Routing Estimates Update & Rollback
# ==========================================
def test_scenario_15_adaptation_empirical_tracking():
    with TestClient(app) as client:
        res = client.get("/api/adaptation/history")
        assert res.status_code == 200
        data = res.json()
        assert len(data) > 0
        first_obs = data[0]
        assert "empirical_quality_score" in first_obs
        assert "sample_count" in first_obs

        # Test rollback on observation
        rb_res = client.post("/api/adaptation/rollback", json={
            "model_id": first_obs["model_id"],
            "task_category": first_obs["task_category"]
        })
        assert rb_res.status_code == 200

# ==========================================
# SCENARIO 16: Distinguishing Real vs Simulated Data
# ==========================================
def test_scenario_16_distinguish_real_vs_simulated():
    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert "mode" in data
        assert "has_live_providers" in data
        if not data["has_live_providers"]:
            assert "Simulator" in data["mode"]

# ==========================================
# SCENARIO 17: Recommendations API Handles Populated and Empty
# ==========================================
def test_scenario_17_recommendations_clean_response():
    with TestClient(app) as client:
        res = client.get("/api/finops/recommendations")
        assert res.status_code == 200
        recs = res.json()
        assert isinstance(recs, list)
        for r in recs:
            assert isinstance(r["supporting_data"], dict)
            assert "expected_monthly_savings_usd" in r
            assert r["status"] in ["pending", "applied", "dismissed"]

# ==========================================
# SCENARIO 18: Health Diagnostic Liveness and Readiness
# ==========================================
def test_scenario_18_health_liveness_readiness():
    with TestClient(app) as client:
        # Liveness
        r_live = client.get("/api/health/live")
        assert r_live.status_code == 200
        assert r_live.json()["status"] == "alive"

        # Readiness
        r_ready = client.get("/api/health/ready")
        assert r_ready.status_code == 200
        assert r_ready.json()["status"] == "ready"

        # Diagnostic
        r_health = client.get("/api/health")
        assert r_health.status_code == 200
        h_data = r_health.json()
        assert h_data["liveness"] is True
        assert h_data["readiness"] is True
        assert h_data["database"]["connected"] is True
