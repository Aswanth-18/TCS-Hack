import datetime
import uuid
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ModelRegistryItem(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, unique=True, nullable=False, index=True) # e.g. "gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False, index=True) # "openai", "anthropic", "google", "groq", "meta"
    tier = Column(String, default="standard") # "flagship", "balanced", "economy", "specialized"
    input_cost_per_m = Column(Float, nullable=False) # In USD per 1,000,000 tokens
    output_cost_per_m = Column(Float, nullable=False) # In USD per 1,000,000 tokens
    latency_p50_ms = Column(Integer, default=600)
    context_window = Column(Integer, default=128000)
    supported_tasks = Column(JSON, default=list) # ["coding", "reasoning", "summarization", "data_analysis", "general_qa", "structured_output"]
    capabilities = Column(JSON, default=list) # ["code", "reasoning", "vision", "json_mode", "function_calling"]
    privacy_tier = Column(String, default="standard") # "standard", "hipaa_eligible", "zero_data_retention", "local_only"
    benchmark_quality_score = Column(Float, default=0.85) # 0.0 to 1.0 (from MMLU/HumanEval/benchmarks)
    reliability_rate = Column(Float, default=0.99) # 0.0 to 1.0
    enabled = Column(Boolean, default=True)
    is_healthy = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))


class RoutingPolicy(Base):
    __tablename__ = "routing_policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    version = Column(Integer, default=1, index=True)
    name = Column(String, default="Default Intelligent Policy")
    description = Column(Text, default="Adaptive cost-quality-latency multi-objective optimization")
    is_active = Column(Boolean, default=True)
    
    # Constraints
    max_budget_per_request = Column(Float, default=0.05)
    min_quality_threshold = Column(Float, default=0.70)
    max_latency_ms = Column(Integer, default=4000)
    fallback_enabled = Column(Boolean, default=True)
    max_retries = Column(Integer, default=2)
    allowed_providers = Column(JSON, default=lambda: ["openai", "anthropic", "google", "groq", "meta"])

    # Multi-objective weights (must sum to 1.0)
    weight_cost = Column(Float, default=0.40)
    weight_quality = Column(Float, default=0.35)
    weight_latency = Column(Float, default=0.15)
    weight_reliability = Column(Float, default=0.10)

    # Strategy: "astraroute_intelligent", "always_advanced", "cheapest_eligible", "rule_based"
    default_strategy = Column(String, default="astraroute_intelligent")

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    applied_by = Column(String, default="system")


class RequestAuditLog(Base):
    __tablename__ = "request_audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    request_id = Column(String, unique=True, index=True, default=generate_uuid)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    prompt = Column(Text, nullable=False)
    task_type = Column(String, nullable=False, index=True) # coding, reasoning, summarization, data_analysis, structured_output, general_qa
    detected_complexity = Column(String, default="moderate") # simple, moderate, complex
    estimated_tokens = Column(Integer, default=500)
    data_sensitivity = Column(String, default="internal") # public, internal, confidential, restricted
    business_criticality = Column(String, default="standard") # standard, high, mission_critical
    
    # User / Policy Constraints Applied
    user_budget_max = Column(Float, nullable=True)
    user_quality_min = Column(Float, nullable=True)
    user_latency_max = Column(Integer, nullable=True)
    
    # Decisions & Scoring
    selected_model_id = Column(String, nullable=False)
    selected_provider = Column(String, nullable=False)
    routing_strategy = Column(String, default="astraroute_intelligent")
    routing_score = Column(Float, default=0.0)
    routing_explanation = Column(Text, default="")
    eligible_models = Column(JSON, default=list) # List of model_ids with preliminary scores
    rejected_models = Column(JSON, default=list) # List of {model_id, reason}

    # Execution telemetry
    execution_status = Column(String, default="success") # success, failed, fallback_success, partially_verified
    total_tokens = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_latency_ms = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    is_simulated = Column(Boolean, default=False)

    # Quality Guardian Verification
    verification_status = Column(String, default="Verified Pass") # Verified Pass, Failed Verification, Partially Verified, Verification Unavailable
    verification_method = Column(String, default="rubric") # unit_test, schema_validation, arithmetic_check, rubric, label_match
    verification_score = Column(Float, default=1.0)
    verification_details = Column(JSON, default=dict) # { passed_checks: [], failed_checks: [], rationale: "" }

    # Fallback tracking
    fallback_occurred = Column(Boolean, default=False)
    attempt_count = Column(Integer, default=1)
    
    # Response
    final_response = Column(Text, default="")
    policy_version = Column(Integer, default=1)

    attempts = relationship("ExecutionAttempt", back_populates="request_log", cascade="all, delete-orphan")


class ExecutionAttempt(Base):
    __tablename__ = "execution_attempts"

    id = Column(String, primary_key=True, default=generate_uuid)
    request_id = Column(String, ForeignKey("request_audit_logs.request_id", ondelete="CASCADE"), index=True)
    attempt_number = Column(Integer, default=1)
    model_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    
    status = Column(String, default="success") # success, error, timeout, rate_limit, verification_failed
    error_message = Column(Text, nullable=True)
    
    latency_ms = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    is_fallback = Column(Boolean, default=False)
    fallback_reason = Column(String, nullable=True)
    
    response_preview = Column(Text, default="")
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    request_log = relationship("RequestAuditLog", back_populates="attempts")


class BenchmarkItem(Base):
    __tablename__ = "benchmark_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    benchmark_id = Column(String, default="standard_suite_v1", index=True)
    task_category = Column(String, nullable=False) # coding, reasoning, summarization, data_analysis, structured_output, general_qa
    difficulty = Column(String, default="moderate") # simple, moderate, complex
    prompt = Column(Text, nullable=False)
    ground_truth = Column(Text, nullable=True) # Expected response, unit tests, or reference
    expected_output_schema = Column(JSON, nullable=True)
    verification_method = Column(String, default="rubric")


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    dataset_name = Column(String, default="Standard FinOps Suite (50 tasks)")
    strategy = Column(String, nullable=False) # always_advanced, cheapest_eligible, rule_based, astraroute_intelligent
    status = Column(String, default="completed") # pending, running, completed, failed
    total_items = Column(Integer, default=0)
    successful_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    total_cost_usd = Column(Float, default=0.0)
    cost_per_successful_outcome = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    avg_quality_score = Column(Float, default=0.0)
    verification_success_rate = Column(Float, default=0.0)
    fallback_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    details = Column(JSON, default=list) # Per-task breakdown


class FinOpsRecommendation(Base):
    __tablename__ = "finops_recommendations"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # "downgrade_opportunity", "caching_candidate", "spending_anomaly", "latency_optimization", "high_failure_risk"
    severity = Column(String, default="medium") # low, medium, high
    issue = Column(Text, nullable=False)
    supporting_data = Column(JSON, default=dict) # metrics, samples, observations
    proposed_action = Column(Text, nullable=False)
    expected_monthly_savings_usd = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.85) # 0.0 to 1.0
    status = Column(String, default="pending") # pending, applied, dismissed
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class AdaptiveObservation(Base):
    __tablename__ = "adaptive_observations"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, nullable=False, index=True)
    task_category = Column(String, nullable=False, index=True)
    sample_count = Column(Integer, default=0)
    empirical_quality_score = Column(Float, default=0.80)
    empirical_latency_ms = Column(Float, default=500.0)
    empirical_cost_usd = Column(Float, default=0.001)
    success_rate = Column(Float, default=1.0)
    last_updated = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    update_history = Column(JSON, default=list) # [{ timestamp, old_score, new_score, reason }]

