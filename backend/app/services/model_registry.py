from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import ModelRegistryItem, RoutingPolicy

DEFAULT_MODELS = [
    {
        "model_id": "gpt-4o",
        "name": "OpenAI GPT-4o",
        "provider": "openai",
        "tier": "flagship",
        "input_cost_per_m": 2.50,
        "output_cost_per_m": 10.00,
        "latency_p50_ms": 650,
        "context_window": 128000,
        "supported_tasks": ["coding", "reasoning", "summarization", "data_analysis", "general_qa", "structured_output"],
        "capabilities": ["code", "reasoning", "vision", "json_mode", "function_calling"],
        "privacy_tier": "zero_data_retention",
        "benchmark_quality_score": 0.93,
        "reliability_rate": 0.995,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "gpt-4o-mini",
        "name": "OpenAI GPT-4o Mini",
        "provider": "openai",
        "tier": "economy",
        "input_cost_per_m": 0.15,
        "output_cost_per_m": 0.60,
        "latency_p50_ms": 380,
        "context_window": 128000,
        "supported_tasks": ["general_qa", "summarization", "coding", "structured_output"],
        "capabilities": ["code", "json_mode", "function_calling"],
        "privacy_tier": "standard",
        "benchmark_quality_score": 0.82,
        "reliability_rate": 0.998,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "claude-3-5-sonnet",
        "name": "Anthropic Claude 3.5 Sonnet",
        "provider": "anthropic",
        "tier": "flagship",
        "input_cost_per_m": 3.00,
        "output_cost_per_m": 15.00,
        "latency_p50_ms": 780,
        "context_window": 200000,
        "supported_tasks": ["coding", "reasoning", "summarization", "data_analysis", "structured_output"],
        "capabilities": ["code", "reasoning", "vision", "json_mode"],
        "privacy_tier": "enterprise",
        "benchmark_quality_score": 0.94,
        "reliability_rate": 0.993,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "claude-3-5-haiku",
        "name": "Anthropic Claude 3.5 Haiku",
        "provider": "anthropic",
        "tier": "economy",
        "input_cost_per_m": 0.80,
        "output_cost_per_m": 4.00,
        "latency_p50_ms": 320,
        "context_window": 200000,
        "supported_tasks": ["general_qa", "summarization", "coding", "structured_output"],
        "capabilities": ["code", "json_mode"],
        "privacy_tier": "enterprise",
        "benchmark_quality_score": 0.84,
        "reliability_rate": 0.996,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "gemini-1.5-pro",
        "name": "Google Gemini 1.5 Pro",
        "provider": "google",
        "tier": "flagship",
        "input_cost_per_m": 1.25,
        "output_cost_per_m": 5.00,
        "latency_p50_ms": 700,
        "context_window": 1000000,
        "supported_tasks": ["coding", "reasoning", "summarization", "data_analysis", "general_qa", "structured_output"],
        "capabilities": ["code", "reasoning", "vision", "json_mode"],
        "privacy_tier": "hipaa_eligible",
        "benchmark_quality_score": 0.91,
        "reliability_rate": 0.991,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "gemini-1.5-flash",
        "name": "Google Gemini 1.5 Flash",
        "provider": "google",
        "tier": "economy",
        "input_cost_per_m": 0.075,
        "output_cost_per_m": 0.30,
        "latency_p50_ms": 220,
        "context_window": 1000000,
        "supported_tasks": ["general_qa", "summarization", "data_analysis", "structured_output"],
        "capabilities": ["code", "json_mode"],
        "privacy_tier": "standard",
        "benchmark_quality_score": 0.81,
        "reliability_rate": 0.997,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "llama-3.3-70b",
        "name": "Meta Llama 3.3 70B (Groq LPU)",
        "provider": "groq",
        "tier": "balanced",
        "input_cost_per_m": 0.59,
        "output_cost_per_m": 0.79,
        "latency_p50_ms": 180,
        "context_window": 128000,
        "supported_tasks": ["coding", "reasoning", "summarization", "data_analysis", "general_qa"],
        "capabilities": ["code", "reasoning", "json_mode"],
        "privacy_tier": "standard",
        "benchmark_quality_score": 0.87,
        "reliability_rate": 0.994,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "deepseek-v3",
        "name": "DeepSeek V3",
        "provider": "deepseek",
        "tier": "economy",
        "input_cost_per_m": 0.14,
        "output_cost_per_m": 0.28,
        "latency_p50_ms": 420,
        "context_window": 64000,
        "supported_tasks": ["coding", "reasoning", "data_analysis", "general_qa", "structured_output"],
        "capabilities": ["code", "reasoning", "json_mode"],
        "privacy_tier": "standard",
        "benchmark_quality_score": 0.88,
        "reliability_rate": 0.985,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "mistral-large",
        "name": "Mistral Large 2",
        "provider": "mistral",
        "tier": "flagship",
        "input_cost_per_m": 2.00,
        "output_cost_per_m": 6.00,
        "latency_p50_ms": 610,
        "context_window": 128000,
        "supported_tasks": ["coding", "reasoning", "data_analysis", "structured_output"],
        "capabilities": ["code", "reasoning", "json_mode"],
        "privacy_tier": "zero_data_retention",
        "benchmark_quality_score": 0.89,
        "reliability_rate": 0.992,
        "enabled": True,
        "is_healthy": True
    },
    {
        "model_id": "local-llama-8b-secure",
        "name": "Local Ollama Llama 3.1 8B (On-Prem)",
        "provider": "local",
        "tier": "specialized",
        "input_cost_per_m": 0.00,
        "output_cost_per_m": 0.00,
        "latency_p50_ms": 280,
        "context_window": 32000,
        "supported_tasks": ["general_qa", "summarization", "coding"],
        "capabilities": ["code"],
        "privacy_tier": "local_only",
        "benchmark_quality_score": 0.77,
        "reliability_rate": 0.999,
        "enabled": True,
        "is_healthy": True
    }
]

class ModelRegistryService:
    @classmethod
    def seed_default_models(cls, db: Session) -> List[ModelRegistryItem]:
        existing = db.query(ModelRegistryItem).all()
        if existing:
            return existing

        created = []
        for m in DEFAULT_MODELS:
            item = ModelRegistryItem(**m)
            db.add(item)
            created.append(item)

        # Also seed default active policy if not exists
        policy = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()
        if not policy:
            p = RoutingPolicy(
                version=1,
                name="AstraRoute Enterprise Standard Policy",
                description="Balanced FinOps policy maximizing quality while cutting inference costs up to 65%",
                is_active=True,
                max_budget_per_request=0.05,
                min_quality_threshold=0.70,
                max_latency_ms=4000,
                weight_cost=0.40,
                weight_quality=0.35,
                weight_latency=0.15,
                weight_reliability=0.10,
                default_strategy="astraroute_intelligent"
            )
            db.add(p)

        db.commit()
        return created

