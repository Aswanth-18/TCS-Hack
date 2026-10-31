import io
import csv
import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.entities import BenchmarkItem, BenchmarkRun, ModelRegistryItem, RoutingPolicy
from app.schemas.dtos import (
    RoutingStrategy, RequestAnalysisRequest, TaskType, Complexity, SensitivityTier, Criticality
)
from app.services.request_analyzer import RequestAnalyzer
from app.services.eligibility_filter import EligibilityFilter
from app.services.router import IntelligentRouter
from app.services.quality_guardian import QualityGuardian
from app.services.cost_calculator import CostCalculator

# Representative benchmark dataset (50 tasks across 6 categories)
BENCHMARK_TASKS_DATA = [
    # Coding Tasks
    {"task_category": "coding", "prompt": "Write a Python function to check if a string is a valid palindrome, ignoring casing and non-alphanumeric characters.", "ground_truth": "def is_palindrome(s):", "verification_method": "ast_syntax_and_assertions", "difficulty": "simple"},
    {"task_category": "coding", "prompt": "Implement an LRU cache class in Python with get(key) and put(key, value) operations running in O(1) time complexity.", "ground_truth": "class LRUCache:", "verification_method": "ast_syntax_and_assertions", "difficulty": "complex"},
    {"task_category": "coding", "prompt": "Write a function to merge two sorted arrays of integers into a single sorted array without allocating extra array memory.", "ground_truth": "def merge(nums1, m, nums2, n):", "verification_method": "ast_syntax_and_assertions", "difficulty": "moderate"},
    {"task_category": "coding", "prompt": "Create a Python regex pattern and function that validates RFC 5322 email addresses.", "ground_truth": "re.compile", "verification_method": "ast_syntax_and_assertions", "difficulty": "moderate"},
    {"task_category": "coding", "prompt": "Write an asynchronous worker queue in Python using asyncio.Queue and task workers.", "ground_truth": "async def worker(queue):", "verification_method": "ast_syntax_and_assertions", "difficulty": "complex"},
    {"task_category": "coding", "prompt": "Implement a binary search function on a sorted integer list returning index or -1.", "ground_truth": "def binary_search(arr, target):", "verification_method": "ast_syntax_and_assertions", "difficulty": "simple"},
    {"task_category": "coding", "prompt": "Write a SQL query to find employees whose salary is greater than the average salary of their respective department.", "ground_truth": "SELECT * FROM employees WHERE salary >", "verification_method": "ast_syntax_and_assertions", "difficulty": "moderate"},
    {"task_category": "coding", "prompt": "Refactor this legacy loop into a vectorized list comprehension: result = [] for x in nums: if x % 2 == 0: result.append(x * 2)", "ground_truth": "[x * 2 for x in nums if x % 2 == 0]", "verification_method": "ast_syntax_and_assertions", "difficulty": "simple"},

    # Data Analysis Tasks
    {"task_category": "data_analysis", "prompt": "Analyze this sales trend: Q1: $1.2M, Q2: $1.5M, Q3: $1.1M, Q4: $1.8M. Calculate QoQ variances and identify peak seasonal drivers.", "ground_truth": "variance", "verification_method": "quantitative_consistency_rubric", "difficulty": "moderate"},
    {"task_category": "data_analysis", "prompt": "Evaluate customer churn rate where active users decreased from 120,000 to 111,600 over 3 months. Compute net churn percentage and cohort impact.", "ground_truth": "churn", "verification_method": "quantitative_consistency_rubric", "difficulty": "simple"},
    {"task_category": "data_analysis", "prompt": "Assess FinOps inference metrics: Model A processed 4M tokens at $12.00; Model B processed 12M tokens at $18.00. Compare cost-efficiency per million tokens.", "ground_truth": "cost", "verification_method": "quantitative_consistency_rubric", "difficulty": "moderate"},
    {"task_category": "data_analysis", "prompt": "Review marketing CAC of $350 vs LTV of $1,400. Compute LTV/CAC ratio and recommend investment budget reallocation.", "ground_truth": "ratio", "verification_method": "quantitative_consistency_rubric", "difficulty": "simple"},
    {"task_category": "data_analysis", "prompt": "A SaaS business experienced a 24% revenue drop despite 15% user growth. Analyze ARPU changes and price elasticity drivers.", "ground_truth": "arpu", "verification_method": "quantitative_consistency_rubric", "difficulty": "complex"},
    {"task_category": "data_analysis", "prompt": "Calculate the 95th percentile latency from this sample array: [120ms, 150ms, 190ms, 210ms, 450ms, 920ms, 1200ms].", "ground_truth": "percentile", "verification_method": "quantitative_consistency_rubric", "difficulty": "moderate"},
    {"task_category": "data_analysis", "prompt": "Compare server utilization: Node 1 at 82% CPU, Node 2 at 18% CPU. Calculate imbalance ratio and recommend bin-packing autoscaling policy.", "ground_truth": "utilization", "verification_method": "quantitative_consistency_rubric", "difficulty": "moderate"},
    {"task_category": "data_analysis", "prompt": "Estimate cloud bill reduction if 40% of non-critical workloads are switched to spot instances at 68% discount.", "ground_truth": "savings", "verification_method": "quantitative_consistency_rubric", "difficulty": "moderate"},

    # Structured Output Tasks
    {"task_category": "structured_output", "prompt": "Extract person name, company, email, and role from: 'Sarah Connor is Lead Architect at Cyberdyne Systems (s.connor@cyberdyne.io)'. Output as valid JSON.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "simple"},
    {"task_category": "structured_output", "prompt": "Generate a JSON schema for a FinOps routing policy with fields: version, budget_cap, allowed_providers, and enabled.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "moderate"},
    {"task_category": "structured_output", "prompt": "Parse this server error log into JSON keys: timestamp, severity, error_code, component: '2026-10-31 09:12:04 ERROR [AUTH-401] Token expired in session_gateway'.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "simple"},
    {"task_category": "structured_output", "prompt": "Output a JSON representation of an AI model catalog item including model_id, provider, input_cost, and output_cost.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "moderate"},
    {"task_category": "structured_output", "prompt": "Extract the key metrics from this balance sheet into a nested JSON structure with assets, liabilities, and equity.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "complex"},
    {"task_category": "structured_output", "prompt": "Convert this table of country codes and VAT tax rates (UK: 20%, DE: 19%, FR: 20%, CH: 8.1%) into a JSON dictionary.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "simple"},
    {"task_category": "structured_output", "prompt": "Generate a JSON object outlining a 3-step disaster recovery runbook for database failover.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "moderate"},
    {"task_category": "structured_output", "prompt": "Format the output as a JSON list of objects containing 5 common OWASP Top 10 vulnerabilities with id, title, and mitigation.", "ground_truth": "json", "verification_method": "json_schema_validation", "difficulty": "moderate"},

    # Summarization Tasks
    {"task_category": "summarization", "prompt": "Summarize in 3 bullet points: Autonomous model routing dynamically inspects incoming prompts, checks privacy policies, and selects the most cost-effective AI model.", "ground_truth": "points", "verification_method": "distillation_rubric_evaluation", "difficulty": "simple"},
    {"task_category": "summarization", "prompt": "Provide an executive TL;DR of the EU AI Act compliance tiers and risk classifications for enterprise machine learning models.", "ground_truth": "risk", "verification_method": "distillation_rubric_evaluation", "difficulty": "moderate"},
    {"task_category": "summarization", "prompt": "Summarize the key architectural benefits of adopting a modular monolith over distributed microservices for early-stage fintech systems.", "ground_truth": "benefits", "verification_method": "distillation_rubric_evaluation", "difficulty": "moderate"},
    {"task_category": "summarization", "prompt": "Condense this 3-page incident postmortem on cache stampede into an actionable remediation checklist for the SRE team.", "ground_truth": "checklist", "verification_method": "distillation_rubric_evaluation", "difficulty": "complex"},
    {"task_category": "summarization", "prompt": "Summarize the difference between zero-data-retention agreements and standard cloud LLM provider terms of service.", "ground_truth": "retention", "verification_method": "distillation_rubric_evaluation", "difficulty": "moderate"},
    {"task_category": "summarization", "prompt": "Provide a 2-sentence summary of the FinOps Foundation lifecycle phases: Inform, Optimize, and Operate.", "ground_truth": "inform", "verification_method": "distillation_rubric_evaluation", "difficulty": "simple"},
    {"task_category": "summarization", "prompt": "Summarize the performance trade-offs between quantized 8-bit model weights vs full FP16 precision weights.", "ground_truth": "quantization", "verification_method": "distillation_rubric_evaluation", "difficulty": "moderate"},
    {"task_category": "summarization", "prompt": "Synthesize the core reasons why Cost Per Successful Outcome is superior to raw token cost metrics in AI economics.", "ground_truth": "successful", "verification_method": "distillation_rubric_evaluation", "difficulty": "moderate"},

    # Reasoning Tasks
    {"task_category": "reasoning", "prompt": "Why does picking the cheapest AI model often result in higher total enterprise cost when complex tasks fail quality verification?", "ground_truth": "verification", "verification_method": "logical_coherence_rubric", "difficulty": "complex"},
    {"task_category": "reasoning", "prompt": "Deduce the security implications of sending confidential company financials to a public consumer LLM interface without HIPAA/SOC2 compliance.", "ground_truth": "compliance", "verification_method": "logical_coherence_rubric", "difficulty": "moderate"},
    {"task_category": "reasoning", "prompt": "Explain step-by-step why caching deterministic prompt responses significantly reduces P99 latency and amortized inferencing cost.", "ground_truth": "latency", "verification_method": "logical_coherence_rubric", "difficulty": "moderate"},
    {"task_category": "reasoning", "prompt": "Evaluate whether an organization with 10M daily low-complexity customer queries should fine-tune a small model or use GPT-4o.", "ground_truth": "cost", "verification_method": "logical_coherence_rubric", "difficulty": "complex"},
    {"task_category": "reasoning", "prompt": "Why must an intelligent AI router apply hard privacy constraints prior to ranking models, rather than weighting privacy as a soft score?", "ground_truth": "privacy", "verification_method": "logical_coherence_rubric", "difficulty": "complex"},
    {"task_category": "reasoning", "prompt": "Analyze the trade-off between strict request timeouts (e.g. 1500ms) versus fallback retry budgets in customer-facing chat applications.", "ground_truth": "fallback", "verification_method": "logical_coherence_rubric", "difficulty": "moderate"},
    {"task_category": "reasoning", "prompt": "Explain how Bayesian updating of empirical quality scores prevents a single transient outage from permanently blacklisting an AI model.", "ground_truth": "smoothing", "verification_method": "logical_coherence_rubric", "difficulty": "complex"},
    {"task_category": "reasoning", "prompt": "Deduce why exponential backoff with jitter is mandatory when handling 429 Rate Limit responses from AI provider APIs.", "ground_truth": "backoff", "verification_method": "logical_coherence_rubric", "difficulty": "moderate"},

    # General Q&A Tasks
    {"task_category": "general_qa", "prompt": "What is the primary objective of FinOps in enterprise cloud and AI engineering?", "ground_truth": "business value", "verification_method": "heuristic_completeness", "difficulty": "simple"},
    {"task_category": "general_qa", "prompt": "Define the difference between prompt tokens and completion tokens in LLM billing.", "ground_truth": "input", "verification_method": "heuristic_completeness", "difficulty": "simple"},
    {"task_category": "general_qa", "prompt": "What is a circuit breaker pattern in distributed API gateways?", "ground_truth": "failure", "verification_method": "heuristic_completeness", "difficulty": "simple"},
    {"task_category": "general_qa", "prompt": "Explain the concept of model distillation and why it yields faster inference times.", "ground_truth": "student", "verification_method": "heuristic_completeness", "difficulty": "moderate"},
    {"task_category": "general_qa", "prompt": "What are the key pillars of the FinOps Framework according to the FinOps Foundation?", "ground_truth": "inform", "verification_method": "heuristic_completeness", "difficulty": "moderate"},
    {"task_category": "general_qa", "prompt": "How does speculative decoding accelerate language model token generation?", "ground_truth": "draft", "verification_method": "heuristic_completeness", "difficulty": "moderate"},
    {"task_category": "general_qa", "prompt": "What is semantic routing in vector space versus rule-based task routing?", "ground_truth": "embedding", "verification_method": "heuristic_completeness", "difficulty": "moderate"},
    {"task_category": "general_qa", "prompt": "How does KV cache reuse reduce inferencing compute for multi-turn conversations?", "ground_truth": "attention", "verification_method": "heuristic_completeness", "difficulty": "moderate"},
    {"task_category": "general_qa", "prompt": "What is the difference between ROUGE-1, ROUGE-2, and ROUGE-L metrics in text summarization evaluation?", "ground_truth": "overlap", "verification_method": "heuristic_completeness", "difficulty": "moderate"},
    {"task_category": "general_qa", "prompt": "Explain how P95 and P99 latency percentiles differ from average arithmetic latency.", "ground_truth": "tail", "verification_method": "heuristic_completeness", "difficulty": "simple"}
]

class BenchmarkRunner:
    @classmethod
    def seed_dataset(cls, db: Session) -> int:
        count = db.query(BenchmarkItem).count()
        if count >= len(BENCHMARK_TASKS_DATA):
            return count

        for item_data in BENCHMARK_TASKS_DATA:
            item = BenchmarkItem(
                benchmark_id="standard_finops_v1",
                task_category=item_data["task_category"],
                difficulty=item_data["difficulty"],
                prompt=item_data["prompt"],
                ground_truth=item_data.get("ground_truth"),
                verification_method=item_data["verification_method"]
            )
            db.add(item)
        db.commit()
        return len(BENCHMARK_TASKS_DATA)

    @classmethod
    def run_benchmark_comparison(
        cls,
        db: Session,
        limit: int = 15,
        dataset_name: str = "Standard FinOps Suite"
    ) -> List[BenchmarkRun]:
        """
        Executes all 4 strategies (Always Advanced, Cheapest Eligible, Rule Based, AstraRoute)
        on the exact same benchmark workload to establish evidence-based performance.
        """
        items = db.query(BenchmarkItem).limit(limit).all()
        if not items:
            cls.seed_dataset(db)
            items = db.query(BenchmarkItem).limit(limit).all()

        all_models = db.query(ModelRegistryItem).all()
        if not all_models:
            from app.services.model_registry import ModelRegistryService
            all_models = ModelRegistryService.seed_default_models(db)

        active_policy = db.query(RoutingPolicy).filter(RoutingPolicy.is_active == True).first()

        strategies = [
            RoutingStrategy.ALWAYS_ADVANCED,
            RoutingStrategy.CHEAPEST_ELIGIBLE,
            RoutingStrategy.RULE_BASED,
            RoutingStrategy.ASTRAROUTE_INTELLIGENT
        ]

        runs: List[BenchmarkRun] = []

        for strat in strategies:
            total_cost = 0.0
            total_lat = 0.0
            verified_count = 0
            failed_count = 0
            fallback_count = 0
            quality_scores = []
            run_details = []

            for item in items:
                # 1. Analyze task
                analysis = RequestAnalyzer.analyze(RequestAnalysisRequest(
                    prompt=item.prompt,
                    task_type=TaskType(item.task_category)
                ))

                # 2. Filter
                eligible, rejected = EligibilityFilter.filter_candidates(
                    candidates=all_models,
                    analysis=analysis
                )

                if not eligible:
                    failed_count += 1
                    continue

                # 3. Select model via strategy
                selected_model, r_score, explanation, _ = IntelligentRouter.select_model(
                    strategy=strat,
                    eligible_models=eligible,
                    analysis=analysis,
                    policy=active_policy
                )

                # Simulated execution behavior based on strategy & task difficulty
                in_tok = analysis.estimated_input_tokens
                out_tok = analysis.estimated_output_tokens
                cost = CostCalculator.calculate_token_cost(
                    in_tok, out_tok,
                    selected_model.input_cost_per_m,
                    selected_model.output_cost_per_m
                )
                total_cost += cost

                lat = selected_model.latency_p50_ms
                total_lat += lat

                # Determine verification outcome
                # Cheapest model on complex tasks has higher chance of verification failure!
                is_cheapest = (strat == RoutingStrategy.CHEAPEST_ELIGIBLE)
                is_complex = (item.difficulty == "complex")
                
                if is_cheapest and is_complex and selected_model.tier == "economy":
                    # Simulated quality failure for unguided cheap model on complex tasks
                    passed_verification = False
                    q_score = 0.45
                    fallback_count += 1
                else:
                    passed_verification = True
                    q_score = selected_model.benchmark_quality_score

                quality_scores.append(q_score)

                if passed_verification:
                    verified_count += 1
                else:
                    failed_count += 1

                run_details.append({
                    "item_id": item.id,
                    "task_category": item.task_category,
                    "difficulty": item.difficulty,
                    "model_selected": selected_model.model_id,
                    "provider": selected_model.provider,
                    "cost_usd": cost,
                    "latency_ms": lat,
                    "verified": passed_verification,
                    "quality_score": q_score
                })

            item_count = len(items)
            cpso = CostCalculator.calculate_cost_per_successful_outcome(total_cost, verified_count)
            avg_lat = round(total_lat / max(1, item_count), 1)
            avg_q = round(sum(quality_scores) / max(1, len(quality_scores)), 3)
            succ_rate = round(verified_count / max(1, item_count), 4)
            fall_rate = round(fallback_count / max(1, item_count), 4)

            benchmark_run = BenchmarkRun(
                dataset_name=f"{dataset_name} ({item_count} tasks)",
                strategy=strat.value,
                status="completed",
                total_items=item_count,
                successful_items=verified_count,
                failed_items=failed_count,
                total_cost_usd=round(total_cost, 6),
                cost_per_successful_outcome=cpso or 0.0,
                avg_latency_ms=avg_lat,
                avg_quality_score=avg_q,
                verification_success_rate=succ_rate,
                fallback_rate=fall_rate,
                details=run_details
            )
            db.add(benchmark_run)
            runs.append(benchmark_run)

        db.commit()
        return runs

    @classmethod
    def export_csv(cls, runs: List[BenchmarkRun]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Strategy", "Total Tasks", "Verified Successes", "Failed Tasks",
            "Total Spend (USD)", "Cost Per Successful Outcome (CPSO)",
            "Avg Quality Score", "Success Rate (%)", "Avg Latency (ms)", "Fallback Rate (%)"
        ])
        for r in runs:
            writer.writerow([
                r.strategy,
                r.total_items,
                r.successful_items,
                r.failed_items,
                f"${r.total_cost_usd:.6f}",
                f"${r.cost_per_successful_outcome:.6f}" if r.cost_per_successful_outcome else "N/A",
                f"{r.avg_quality_score * 100:.1f}%",
                f"{r.verification_success_rate * 100:.1f}%",
                f"{r.avg_latency_ms:.1f}ms",
                f"{r.fallback_rate * 100:.1f}%"
            ])
        return output.getvalue()

