from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import datetime

class TaskType(str, Enum):
    CODING = "coding"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"
    DATA_ANALYSIS = "data_analysis"
    STRUCTURED_OUTPUT = "structured_output"
    GENERAL_QA = "general_qa"

class Complexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class SensitivityTier(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class Criticality(str, Enum):
    STANDARD = "standard"
    HIGH = "high"
    MISSION_CRITICAL = "mission_critical"

class RoutingStrategy(str, Enum):
    ASTRAROUTE_INTELLIGENT = "astraroute_intelligent"
    ALWAYS_ADVANCED = "always_advanced"
    CHEAPEST_ELIGIBLE = "cheapest_eligible"
    RULE_BASED = "rule_based"

class VerificationStatus(str, Enum):
    VERIFIED_PASS = "Verified Pass"
    FAILED_VERIFICATION = "Failed Verification"
    PARTIALLY_VERIFIED = "Partially Verified"
    VERIFICATION_UNAVAILABLE = "Verification Unavailable"

# --- Analysis Schemas ---
class RequestAnalysisRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User prompt to analyze")
    task_type: Optional[TaskType] = None
    max_budget: Optional[float] = None
    min_quality: Optional[float] = None
    max_latency: Optional[int] = None
    sensitivity: Optional[SensitivityTier] = SensitivityTier.INTERNAL
    criticality: Optional[Criticality] = Criticality.STANDARD
    allowed_providers: Optional[List[str]] = None
    required_capabilities: Optional[List[str]] = None

class RequestAnalysisResponse(BaseModel):
    detected_task_type: TaskType
    detected_complexity: Complexity
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    sensitivity: SensitivityTier
    criticality: Criticality
    required_quality_target: float
    budget_limit_usd: float
    latency_limit_ms: int
    analysis_rationale: str
    classification_uncertainty: float = 0.05
    required_capabilities: List[str]

# --- Model Schemas ---
class ModelDTO(BaseModel):
    id: Optional[str] = None
    model_id: str
    name: str
    provider: str
    tier: str = "standard"
    input_cost_per_m: float
    output_cost_per_m: float
    latency_p50_ms: int = 600
    context_window: int = 128000
    supported_tasks: Optional[List[str]] = []
    capabilities: Optional[List[str]] = []
    privacy_tier: str = "standard"
    benchmark_quality_score: float = 0.85
    reliability_rate: float = 0.99
    enabled: bool = True
    is_healthy: bool = True

class ModelUpdateDTO(BaseModel):
    name: Optional[str] = None
    tier: Optional[str] = None
    enabled: Optional[bool] = None
    is_healthy: Optional[bool] = None
    input_cost_per_m: Optional[float] = None
    output_cost_per_m: Optional[float] = None
    benchmark_quality_score: Optional[float] = None
    latency_p50_ms: Optional[int] = None
    context_window: Optional[int] = None
    privacy_tier: Optional[str] = None
    capabilities: Optional[List[str]] = None
    supported_tasks: Optional[List[str]] = None

# --- Routing Filter Schemas ---
class RejectionReason(BaseModel):
    model_id: str
    reason: str
    category: str # "privacy_policy_violation", "budget_limit_exceeded", "latency_exceeded", "unsupported_capability", "provider_unavailable", "insufficient_quality"

class EligibilityResultDTO(BaseModel):
    eligible_models: List[str]
    rejected_models: List[RejectionReason]

# --- Execution Schemas ---
class ExecuteRequestDTO(BaseModel):
    prompt: str
    task_type: Optional[TaskType] = None
    max_budget: Optional[float] = None
    min_quality: Optional[float] = None
    max_latency: Optional[int] = None
    sensitivity: Optional[SensitivityTier] = SensitivityTier.INTERNAL
    criticality: Optional[Criticality] = Criticality.STANDARD
    strategy: Optional[RoutingStrategy] = RoutingStrategy.ASTRAROUTE_INTELLIGENT
    allowed_providers: Optional[List[str]] = None
    simulate_failure_attempt: Optional[bool] = False # For demonstrating fallback recovery

class AttemptDTO(BaseModel):
    attempt_number: int
    model_id: str
    provider: str
    status: str
    error_message: Optional[str] = None
    latency_ms: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    is_fallback: bool
    fallback_reason: Optional[str] = None
    response_preview: str

class VerificationReportDTO(BaseModel):
    status: VerificationStatus
    method: str
    score: float
    passed_checks: List[str]
    failed_checks: List[str]
    rationale: str
    uncertainty: float = 0.05

class ExecuteResponseDTO(BaseModel):
    request_id: str
    timestamp: str
    prompt: str
    task_type: str
    detected_complexity: str
    selected_model_id: str
    selected_provider: str
    routing_strategy: str
    routing_score: float
    routing_explanation: str
    eligible_models: List[str]
    rejected_models: List[RejectionReason]
    execution_status: str
    total_tokens: int
    input_tokens: int
    output_tokens: int
    total_latency_ms: int
    total_cost_usd: float
    is_simulated: bool
    final_response: str
    verification: VerificationReportDTO
    fallback_occurred: bool
    attempt_count: int
    attempts: List[AttemptDTO]
    policy_version: int

# --- FinOps Summary Schemas ---
class FinOpsSummaryDTO(BaseModel):
    total_requests: int
    verified_success_rate: float
    total_spend_usd: float
    cost_per_successful_outcome: Optional[float] = None
    average_latency_ms: float
    total_tokens: int
    fallback_rate: float
    budget_utilization_pct: float
    spend_by_provider: Dict[str, float]
    spend_by_model: Dict[str, float]
    spend_by_task: Dict[str, float]
    strategy_comparison: List[Dict[str, Any]]

# --- Policy Simulator Schemas ---
class PolicySimulateRequest(BaseModel):
    max_budget_per_request: float
    min_quality_threshold: float
    max_latency_ms: int
    weight_cost: float
    weight_quality: float
    weight_latency: float
    weight_reliability: float
    disabled_providers: Optional[List[str]] = None

class PolicySimulateResponse(BaseModel):
    current_policy: Dict[str, Any]
    proposed_policy: Dict[str, Any]
    projected_spend_usd: float
    projected_savings_pct: float
    projected_quality_score: float
    projected_avg_latency_ms: float
    projected_model_distribution: Dict[str, float]
    projected_budget_violations_pct: float
    trade_off_analysis: str
    warnings: List[str]

# --- Adaptive Learning Schemas ---
class AdaptiveObservationDTO(BaseModel):
    model_id: str
    task_category: str
    sample_count: int
    empirical_quality_score: float
    empirical_latency_ms: float
    empirical_cost_usd: float
    success_rate: float
    last_updated: str
    update_history: List[Dict[str, Any]]

class AdaptiveRollbackRequest(BaseModel):
    model_id: str
    task_category: str

