-- AstraRoute AI: Supabase PostgreSQL Schema
-- Challenge 05: Autonomous AI FinOps & Intelligent Model Routing

-- 1. Models Registry Table
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    model_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    tier TEXT DEFAULT 'standard',
    input_cost_per_m DOUBLE PRECISION NOT NULL,
    output_cost_per_m DOUBLE PRECISION NOT NULL,
    latency_p50_ms INTEGER DEFAULT 600,
    context_window INTEGER DEFAULT 128000,
    supported_tasks JSONB DEFAULT '[]'::jsonb,
    capabilities JSONB DEFAULT '[]'::jsonb,
    privacy_tier TEXT DEFAULT 'standard',
    benchmark_quality_score DOUBLE PRECISION DEFAULT 0.85,
    reliability_rate DOUBLE PRECISION DEFAULT 0.99,
    enabled BOOLEAN DEFAULT true,
    is_healthy BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_models_provider ON models (provider);
CREATE INDEX IF NOT EXISTS idx_models_model_id ON models (model_id);

-- 2. Routing Policies Table
CREATE TABLE IF NOT EXISTS routing_policies (
    id TEXT PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1,
    name TEXT DEFAULT 'Default Intelligent Policy',
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    max_budget_per_request DOUBLE PRECISION DEFAULT 0.05,
    min_quality_threshold DOUBLE PRECISION DEFAULT 0.70,
    max_latency_ms INTEGER DEFAULT 4000,
    fallback_enabled BOOLEAN DEFAULT true,
    max_retries INTEGER DEFAULT 2,
    allowed_providers JSONB DEFAULT '["openai", "anthropic", "google", "groq", "meta"]'::jsonb,
    weight_cost DOUBLE PRECISION DEFAULT 0.40,
    weight_quality DOUBLE PRECISION DEFAULT 0.35,
    weight_latency DOUBLE PRECISION DEFAULT 0.15,
    weight_reliability DOUBLE PRECISION DEFAULT 0.10,
    default_strategy TEXT DEFAULT 'astraroute_intelligent',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    applied_by TEXT DEFAULT 'system'
);

-- 3. Request Audit Logs Table
CREATE TABLE IF NOT EXISTS request_audit_logs (
    id TEXT PRIMARY KEY,
    request_id TEXT UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    prompt TEXT NOT NULL,
    task_type TEXT NOT NULL,
    detected_complexity TEXT DEFAULT 'moderate',
    estimated_tokens INTEGER DEFAULT 500,
    data_sensitivity TEXT DEFAULT 'internal',
    business_criticality TEXT DEFAULT 'standard',
    user_budget_max DOUBLE PRECISION,
    user_quality_min DOUBLE PRECISION,
    user_latency_max INTEGER,
    selected_model_id TEXT NOT NULL,
    selected_provider TEXT NOT NULL,
    routing_strategy TEXT DEFAULT 'astraroute_intelligent',
    routing_score DOUBLE PRECISION DEFAULT 0.0,
    routing_explanation TEXT DEFAULT '',
    eligible_models JSONB DEFAULT '[]'::jsonb,
    rejected_models JSONB DEFAULT '[]'::jsonb,
    execution_status TEXT DEFAULT 'success',
    total_tokens INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_latency_ms INTEGER DEFAULT 0,
    total_cost_usd DOUBLE PRECISION DEFAULT 0.0,
    is_simulated BOOLEAN DEFAULT false,
    verification_status TEXT DEFAULT 'Verified Pass',
    verification_method TEXT DEFAULT 'rubric',
    verification_score DOUBLE PRECISION DEFAULT 1.0,
    verification_details JSONB DEFAULT '{}'::jsonb,
    fallback_occurred BOOLEAN DEFAULT false,
    attempt_count INTEGER DEFAULT 1,
    final_response TEXT DEFAULT '',
    policy_version INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_audit_req_id ON request_audit_logs (request_id);
CREATE INDEX IF NOT EXISTS idx_audit_task ON request_audit_logs (task_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON request_audit_logs (timestamp);

-- 4. Execution Attempts Table (Fallback tracking)
CREATE TABLE IF NOT EXISTS execution_attempts (
    id TEXT PRIMARY KEY,
    request_id TEXT REFERENCES request_audit_logs(request_id) ON DELETE CASCADE,
    attempt_number INTEGER DEFAULT 1,
    model_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    latency_ms INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_usd DOUBLE PRECISION DEFAULT 0.0,
    is_fallback BOOLEAN DEFAULT false,
    fallback_reason TEXT,
    response_preview TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
CREATE INDEX IF NOT EXISTS idx_attempts_request_id ON execution_attempts (request_id);

-- 5. Benchmark Dataset & Runs
CREATE TABLE IF NOT EXISTS benchmark_items (
    id TEXT PRIMARY KEY,
    benchmark_id TEXT DEFAULT 'standard_finops_v1',
    task_category TEXT NOT NULL,
    difficulty TEXT DEFAULT 'moderate',
    prompt TEXT NOT NULL,
    ground_truth TEXT,
    expected_output_schema JSONB,
    verification_method TEXT DEFAULT 'rubric'
);

CREATE TABLE IF NOT EXISTS benchmark_runs (
    id TEXT PRIMARY KEY,
    dataset_name TEXT,
    strategy TEXT NOT NULL,
    status TEXT DEFAULT 'completed',
    total_items INTEGER DEFAULT 0,
    successful_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    total_cost_usd DOUBLE PRECISION DEFAULT 0.0,
    cost_per_successful_outcome DOUBLE PRECISION DEFAULT 0.0,
    avg_latency_ms DOUBLE PRECISION DEFAULT 0.0,
    avg_quality_score DOUBLE PRECISION DEFAULT 0.0,
    verification_success_rate DOUBLE PRECISION DEFAULT 0.0,
    fallback_rate DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    details JSONB DEFAULT '[]'::jsonb
);

-- 6. FinOps Recommendations Table
CREATE TABLE IF NOT EXISTS finops_recommendations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT DEFAULT 'medium',
    issue TEXT NOT NULL,
    supporting_data JSONB DEFAULT '{}'::jsonb,
    proposed_action TEXT NOT NULL,
    expected_monthly_savings_usd DOUBLE PRECISION DEFAULT 0.0,
    confidence_score DOUBLE PRECISION DEFAULT 0.85,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 7. Adaptive Learning Observations Table
CREATE TABLE IF NOT EXISTS adaptive_observations (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    task_category TEXT NOT NULL,
    sample_count INTEGER DEFAULT 0,
    empirical_quality_score DOUBLE PRECISION DEFAULT 0.80,
    empirical_latency_ms DOUBLE PRECISION DEFAULT 500.0,
    empirical_cost_usd DOUBLE PRECISION DEFAULT 0.001,
    success_rate DOUBLE PRECISION DEFAULT 1.0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    update_history JSONB DEFAULT '[]'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_adaptive_model_task ON adaptive_observations (model_id, task_category);

