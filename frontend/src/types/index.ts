export type TaskType = 
  | 'coding' 
  | 'reasoning' 
  | 'summarization' 
  | 'data_analysis' 
  | 'structured_output' 
  | 'general_qa';

export type Complexity = 'simple' | 'moderate' | 'complex';
export type SensitivityTier = 'public' | 'internal' | 'confidential' | 'restricted';
export type Criticality = 'standard' | 'high' | 'mission_critical';
export type RoutingStrategy = 'astraroute_intelligent' | 'always_advanced' | 'cheapest_eligible' | 'rule_based';
export type VerificationStatus = 'Verified Pass' | 'Failed Verification' | 'Partially Verified' | 'Verification Unavailable';

export interface RequestAnalysis {
  detected_task_type: TaskType;
  detected_complexity: Complexity;
  estimated_input_tokens: number;
  estimated_output_tokens: number;
  estimated_total_tokens: number;
  sensitivity: SensitivityTier;
  criticality: Criticality;
  required_quality_target: number;
  budget_limit_usd: number;
  latency_limit_ms: number;
  analysis_rationale: string;
  classification_uncertainty: number;
  required_capabilities: string[];
}

export interface ModelItem {
  id?: string;
  model_id: string;
  name: string;
  provider: string;
  tier: string;
  input_cost_per_m: number;
  output_cost_per_m: number;
  latency_p50_ms: number;
  context_window: number;
  supported_tasks: string[];
  capabilities: string[];
  privacy_tier: string;
  benchmark_quality_score: number;
  reliability_rate: number;
  enabled: boolean;
  is_healthy: boolean;
}

export interface RejectionReason {
  model_id: string;
  reason: string;
  category: string;
}

export interface ExecutionAttempt {
  attempt_number: number;
  model_id: string;
  provider: string;
  status: string;
  error_message?: string;
  latency_ms: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  is_fallback: boolean;
  fallback_reason?: string;
  response_preview: string;
}

export interface VerificationReport {
  status: VerificationStatus;
  method: string;
  score: number;
  passed_checks: string[];
  failed_checks: string[];
  rationale: string;
  uncertainty: number;
}

export interface ExecutionResponse {
  request_id: string;
  timestamp: string;
  prompt: string;
  task_type: string;
  detected_complexity: string;
  selected_model_id: string;
  selected_provider: string;
  routing_strategy: string;
  routing_score: number;
  routing_explanation: string;
  eligible_models: string[];
  rejected_models: RejectionReason[];
  execution_status: string;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  total_latency_ms: number;
  total_cost_usd: number;
  is_simulated: boolean;
  final_response: string;
  verification: VerificationReport;
  fallback_occurred: boolean;
  attempt_count: number;
  attempts: ExecutionAttempt[];
  policy_version: number;
}

export interface FinOpsSummary {
  total_requests: number;
  verified_success_rate: number;
  total_spend_usd: number;
  cost_per_successful_outcome: number | null;
  average_latency_ms: number;
  total_tokens: number;
  fallback_rate: number;
  budget_utilization_pct: number;
  spend_by_provider: Record<string, number>;
  spend_by_model: Record<string, number>;
  spend_by_task: Record<string, number>;
  strategy_comparison: Array<{
    strategy: string;
    request_count: number;
    total_spend_usd: number;
    avg_latency_ms: number;
    verified_successes: number;
    success_rate: number;
    cost_per_successful_outcome: number | null;
  }>;
}

export interface BenchmarkRunItem {
  id: string;
  dataset_name: string;
  strategy: string;
  status: string;
  total_items: number;
  successful_items: number;
  failed_items: number;
  total_cost_usd: number;
  cost_per_successful_outcome: number;
  avg_latency_ms: number;
  avg_quality_score: number;
  verification_success_rate: number;
  fallback_rate: number;
  created_at: string;
  details: Array<{
    item_id: string;
    task_category: string;
    difficulty: string;
    model_selected: string;
    provider: string;
    cost_usd: number;
    latency_ms: number;
    verified: boolean;
    quality_score: number;
  }>;
}

export interface FinOpsRecommendation {
  id: string;
  title: string;
  category: string;
  severity: 'low' | 'medium' | 'high';
  issue: string;
  supporting_data: Record<string, any>;
  proposed_action: string;
  expected_monthly_savings_usd: number;
  confidence_score: number;
  status: 'pending' | 'applied' | 'dismissed';
  created_at: string;
}

export interface AdaptiveObservation {
  model_id: string;
  task_category: string;
  sample_count: number;
  empirical_quality_score: number;
  empirical_latency_ms: number;
  empirical_cost_usd: number;
  success_rate: number;
  last_updated: string;
  update_history: Array<{
    timestamp: string;
    old_score: number;
    new_score: number;
    reason: string;
  }>;
}

export interface SystemHealth {
  status: string;
  app_name: string;
  version: string;
  mode: string;
  has_live_providers: boolean;
  providers: Record<string, boolean>;
  database: {
    connected: boolean;
    engine: string;
    models_registered: number;
  };
  active_policy: {
    version: number;
    strategy: string;
  };
}
