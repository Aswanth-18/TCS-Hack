import re
from typing import Optional, List, Dict, Any
from app.schemas.dtos import (
    RequestAnalysisRequest, RequestAnalysisResponse,
    TaskType, Complexity, SensitivityTier, Criticality
)
from app.services.cost_calculator import CostCalculator

class RequestAnalyzer:
    """
    Module 1: Request & Policy Analyzer.
    Analyzes prompts, detects task category, complexity, sensitivity,
    estimates token usage, and defines deterministic policy constraints.
    """

    # Keyword patterns for task classification
    TASK_PATTERNS = {
        TaskType.CODING: [
            r"\b(def|class|function|import|return|const|let|var|sql|select|query|bug|fix|refactor|python|javascript|typescript|c\+\+|java|rust|html|css|dockerfile|git|algorithm|unit\s*test|implement|regex)\b",
            r"```[a-z]*"
        ],
        TaskType.DATA_ANALYSIS: [
            r"\b(sales|revenue|profit|growth|metric|churn|kpi|dataset|csv|trend|percentage|increase|decrease|forecast|statistical|mean|median|variance|correlation|analysis|analytics|table|chart|roi)\b"
        ],
        TaskType.STRUCTURED_OUTPUT: [
            r"\b(json|xml|yaml|schema|key-value|format as|output as|csv format|structured|pydantic|keys|properties|fields)\b"
        ],
        TaskType.SUMMARIZATION: [
            r"\b(summarize|summary|tldr|tld;dr|brief|condense|abstract|key takeaways|bullet points|nutshell|overview of)\b"
        ],
        TaskType.REASONING: [
            r"\b(why|prove|logic|reason|deduce|infer|step-by-step|evaluate|tradeoff|pros and cons|conclude|implication|puzzle|riddle|hypothesis)\b"
        ]
    }

    # Sensitivity detection patterns
    SENSITIVITY_PATTERNS = {
        SensitivityTier.RESTRICTED: [
            r"\b(ssn|social security|credit card|cvv|password|secret_key|private_key|token|auth_token|bearer|api_key|bank account|routing number)\b",
            r"\b\d{3}-\d{2}-\d{4}\b", # SSN format
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b" # Credit card format
        ],
        SensitivityTier.CONFIDENTIAL: [
            r"\b(confidential|strictly private|nda|proprietary|financial results|internal audit|salary|compensation|merger|acquisition|trade secret)\b"
        ],
        SensitivityTier.INTERNAL: [
            r"\b(internal only|employee|company|internal doc|team only|slack|jira|confluence|roadmap|sprint)\b"
        ]
    }

    @classmethod
    def analyze(cls, req: RequestAnalysisRequest) -> RequestAnalysisResponse:
        prompt_lower = req.prompt.lower()

        # 1. Detect Task Type
        detected_task = req.task_type
        classification_uncertainty = 0.05

        if not detected_task:
            task_scores: Dict[TaskType, int] = {t: 0 for t in TaskType}
            for t_type, patterns in cls.TASK_PATTERNS.items():
                for pat in patterns:
                    matches = len(re.findall(pat, prompt_lower))
                    task_scores[t_type] += matches

            best_match, max_score = max(task_scores.items(), key=lambda item: item[1])
            if max_score > 0:
                detected_task = best_match
                classification_uncertainty = max(0.05, 0.40 - (max_score * 0.08))
            else:
                detected_task = TaskType.GENERAL_QA
                classification_uncertainty = 0.25

        # 2. Detect Complexity
        word_count = len(req.prompt.split())
        has_multi_step = bool(re.search(r"(\b1\..*2\.|first.*second|step 1|additionally|moreover|furthermore)\b", prompt_lower))
        has_code_block = "```" in req.prompt or len(re.findall(r"[{}();<>=]", req.prompt)) > 10
        has_complex_keywords = bool(re.search(r"\b(asynchronous|deadlock|concurrency|lru|cache|backpressure|distributed|algorithm|variance|elasticity|architecture)\b", prompt_lower))

        if word_count > 150 or (has_multi_step and (has_code_block or has_complex_keywords)) or has_complex_keywords or (detected_task in [TaskType.CODING, TaskType.REASONING] and (word_count > 40 or has_multi_step)):
            detected_complexity = Complexity.COMPLEX
        elif word_count > 25 or has_multi_step or detected_task in [TaskType.DATA_ANALYSIS, TaskType.STRUCTURED_OUTPUT]:
            detected_complexity = Complexity.MODERATE
        else:
            detected_complexity = Complexity.SIMPLE

        # 3. Detect Sensitivity
        detected_sensitivity = req.sensitivity or SensitivityTier.INTERNAL
        # Inspect prompt to auto-escalate if secret patterns detected
        for tier in [SensitivityTier.RESTRICTED, SensitivityTier.CONFIDENTIAL, SensitivityTier.INTERNAL]:
            patterns = cls.SENSITIVITY_PATTERNS.get(tier, [])
            if any(re.search(pat, prompt_lower) for pat in patterns):
                # Escalate if detected tier is higher than requested
                tier_order = [SensitivityTier.PUBLIC, SensitivityTier.INTERNAL, SensitivityTier.CONFIDENTIAL, SensitivityTier.RESTRICTED]
                if tier_order.index(tier) > tier_order.index(detected_sensitivity):
                    detected_sensitivity = tier
                break

        # 4. Criticality
        criticality = req.criticality or Criticality.STANDARD
        if detected_sensitivity == SensitivityTier.RESTRICTED and criticality == Criticality.STANDARD:
            criticality = Criticality.HIGH

        # 5. Estimate Tokens
        token_estimates = CostCalculator.estimate_tokens_from_prompt(req.prompt, detected_task.value)

        # 6. Quality & Budget Targets
        quality_map = {
            (Complexity.SIMPLE, Criticality.STANDARD): 0.65,
            (Complexity.SIMPLE, Criticality.HIGH): 0.75,
            (Complexity.SIMPLE, Criticality.MISSION_CRITICAL): 0.85,
            (Complexity.MODERATE, Criticality.STANDARD): 0.75,
            (Complexity.MODERATE, Criticality.HIGH): 0.85,
            (Complexity.MODERATE, Criticality.MISSION_CRITICAL): 0.90,
            (Complexity.COMPLEX, Criticality.STANDARD): 0.85,
            (Complexity.COMPLEX, Criticality.HIGH): 0.90,
            (Complexity.COMPLEX, Criticality.MISSION_CRITICAL): 0.95,
        }
        required_quality = req.min_quality or quality_map.get((detected_complexity, criticality), 0.75)

        # Budget ceiling default based on complexity and tokens
        default_budget = req.max_budget or (0.015 if detected_complexity == Complexity.SIMPLE else (0.04 if detected_complexity == Complexity.MODERATE else 0.10))
        latency_ceiling = req.max_latency or (2500 if detected_complexity == Complexity.SIMPLE else (4500 if detected_complexity == Complexity.MODERATE else 8000))

        # Required capabilities
        capabilities: List[str] = []
        if detected_task == TaskType.CODING:
            capabilities.append("code")
        if detected_task in [TaskType.REASONING, TaskType.DATA_ANALYSIS]:
            capabilities.append("reasoning")
        if detected_task == TaskType.STRUCTURED_OUTPUT:
            capabilities.append("json_mode")

        rationale = (
            f"Classified as '{detected_task.value}' with '{detected_complexity.value}' complexity "
            f"based on linguistic markers and structural syntax ({word_count} words). "
            f"Data sensitivity is '{detected_sensitivity.value}' and business criticality is '{criticality.value}'. "
            f"Required quality target is set to {int(required_quality * 100)}% with max budget ${default_budget:.3f}."
        )

        return RequestAnalysisResponse(
            detected_task_type=detected_task,
            detected_complexity=detected_complexity,
            estimated_input_tokens=token_estimates["estimated_input_tokens"],
            estimated_output_tokens=token_estimates["estimated_output_tokens"],
            estimated_total_tokens=token_estimates["estimated_total_tokens"],
            sensitivity=detected_sensitivity,
            criticality=criticality,
            required_quality_target=required_quality,
            budget_limit_usd=default_budget,
            latency_limit_ms=latency_ceiling,
            analysis_rationale=rationale,
            classification_uncertainty=round(classification_uncertainty, 2),
            required_capabilities=capabilities
        )

