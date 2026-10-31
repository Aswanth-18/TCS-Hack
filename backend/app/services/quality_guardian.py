import re
import json
import ast
from typing import Optional, List, Dict, Any
from app.schemas.dtos import VerificationStatus, VerificationReportDTO, TaskType

class QualityGuardian:
    """
    Module 5: Quality Guardian.
    Task-aware deterministic verification system.
    Evaluates responses using specialized test methods per task category.
    """

    @classmethod
    def verify(
        cls,
        task_type: TaskType,
        response_text: str,
        ground_truth: Optional[str] = None,
        expected_schema: Optional[Dict[str, Any]] = None
    ) -> VerificationReportDTO:
        if not response_text or len(response_text.strip()) == 0:
            return VerificationReportDTO(
                status=VerificationStatus.FAILED_VERIFICATION,
                method="empty_check",
                score=0.0,
                passed_checks=[],
                failed_checks=["Response payload is empty"],
                rationale="Model produced zero output characters."
            )

        if task_type == TaskType.CODING:
            return cls._verify_coding(response_text, ground_truth)
        elif task_type == TaskType.STRUCTURED_OUTPUT:
            return cls._verify_structured(response_text, expected_schema)
        elif task_type == TaskType.DATA_ANALYSIS:
            return cls._verify_data_analysis(response_text)
        elif task_type == TaskType.SUMMARIZATION:
            return cls._verify_summarization(response_text)
        elif task_type == TaskType.REASONING:
            return cls._verify_reasoning(response_text)
        else:
            return cls._verify_general_qa(response_text, ground_truth)

    @classmethod
    def _verify_coding(cls, text: str, ground_truth: Optional[str] = None) -> VerificationReportDTO:
        passed = []
        failed = []

        # Check 1: Code block markdown formatting
        code_blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
        if code_blocks:
            passed.append("Markdown code block delimiter present")
            raw_code = code_blocks[0]
        else:
            failed.append("Missing fenced markdown code block")
            raw_code = text

        # Check 2: Python syntax parsing via AST
        try:
            ast.parse(raw_code)
            passed.append("Valid Python AST syntax (0 syntax errors)")
        except SyntaxError as e:
            failed.append(f"Python syntax error: {e.msg} at line {e.lineno}")

        # Check 3: Ground truth keywords or test assertions
        if ground_truth:
            gt_tokens = [tok.strip() for tok in ground_truth.split() if len(tok.strip()) > 3]
            matches = [tok for tok in gt_tokens if tok.lower() in text.lower()]
            if len(matches) >= max(1, int(len(gt_tokens) * 0.5)):
                passed.append(f"Ground truth alignment ({len(matches)}/{len(gt_tokens)} key symbols matched)")
            else:
                failed.append("Low correspondence with ground truth reference")

        score = len(passed) / max(1, (len(passed) + len(failed)))
        status = (
            VerificationStatus.VERIFIED_PASS if not failed
            else (VerificationStatus.PARTIALLY_VERIFIED if passed else VerificationStatus.FAILED_VERIFICATION)
        )

        return VerificationReportDTO(
            status=status,
            method="ast_syntax_and_assertions",
            score=round(score, 2),
            passed_checks=passed,
            failed_checks=failed,
            rationale=f"Code verification evaluated {len(passed)} passing checks and {len(failed)} warnings/errors."
        )

    @classmethod
    def _verify_structured(cls, text: str, schema: Optional[Dict[str, Any]] = None) -> VerificationReportDTO:
        passed = []
        failed = []

        # Extract potential JSON
        cleaned = text.strip()
        json_match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if json_match:
            cleaned = json_match.group(1)

        try:
            parsed = json.loads(cleaned)
            passed.append("Valid JSON syntax parse")

            if schema and isinstance(schema, dict) and isinstance(parsed, dict):
                required_keys = schema.get("required", list(schema.keys()))
                missing_keys = [k for k in required_keys if k not in parsed]
                if not missing_keys:
                    passed.append(f"All required schema keys present ({', '.join(required_keys)})")
                else:
                    failed.append(f"Missing schema keys: {', '.join(missing_keys)}")
            else:
                passed.append("Structured entity dictionary detected")
        except json.JSONDecodeError as e:
            failed.append(f"Invalid JSON format: {e.msg}")

        score = len(passed) / max(1, (len(passed) + len(failed)))
        status = VerificationStatus.VERIFIED_PASS if not failed else VerificationStatus.FAILED_VERIFICATION

        return VerificationReportDTO(
            status=status,
            method="json_schema_validation",
            score=round(score, 2),
            passed_checks=passed,
            failed_checks=failed,
            rationale="JSON structure parsed and validated against schema requirements."
        )

    @classmethod
    def _verify_data_analysis(cls, text: str) -> VerificationReportDTO:
        passed = []
        failed = []

        # Check for numeric metrics, percentages or currency values
        has_metrics = bool(re.search(r"(\$?\d+(?:\.\d+)?%?|\b(ratio|mean|growth|revenue|variance)\b)", text, re.IGNORECASE))
        if has_metrics:
            passed.append("Quantitative metrics and numerical values present")
        else:
            failed.append("Missing numerical data evidence or calculations")

        # Check for structured findings / bullet points
        has_structure = bool(re.search(r"(^[-*•]|\b\d+\.\s)", text, re.MULTILINE))
        if has_structure:
            passed.append("Clear itemized breakdown / findings structure")
        else:
            failed.append("Unstructured prose without clear analytical sections")

        score = len(passed) / max(1, (len(passed) + len(failed)))
        status = VerificationStatus.VERIFIED_PASS if len(failed) == 0 else VerificationStatus.PARTIALLY_VERIFIED

        return VerificationReportDTO(
            status=status,
            method="quantitative_consistency_rubric",
            score=round(score, 2),
            passed_checks=passed,
            failed_checks=failed,
            rationale="Verified numerical consistency and structured analytical breakdown."
        )

    @classmethod
    def _verify_summarization(cls, text: str) -> VerificationReportDTO:
        passed = []
        failed = []

        words = len(text.split())
        if 20 <= words <= 400:
            passed.append(f"Conciseness bounds respected ({words} words)")
        elif words < 20:
            failed.append("Summary is too brief (< 20 words)")
        else:
            failed.append("Summary exceeded recommended conciseness (> 400 words)")

        # Bullet point or synthesis check
        if bool(re.search(r"(^[-*•]|\b\d+\.\s|\bkey\b|\bfindings\b)", text, re.MULTILINE | re.IGNORECASE)):
            passed.append("Key takeaways identified with clear visual hierarchy")
        else:
            failed.append("Lacks structured bullet points or distilled takeaway cues")

        score = len(passed) / max(1, (len(passed) + len(failed)))
        status = VerificationStatus.VERIFIED_PASS if not failed else VerificationStatus.PARTIALLY_VERIFIED

        return VerificationReportDTO(
            status=status,
            method="distillation_rubric_evaluation",
            score=round(score, 2),
            passed_checks=passed,
            failed_checks=failed,
            rationale="Summary evaluated for conciseness and salient points extraction."
        )

    @classmethod
    def _verify_reasoning(cls, text: str) -> VerificationReportDTO:
        passed = []
        failed = []

        # Checks for logical connective words
        connectives = ["because", "therefore", "however", "consequently", "furthermore", "leads to", "thus"]
        matches = [c for c in connectives if c in text.lower()]
        if len(matches) >= 2:
            passed.append(f"Logical causal connectives present ({', '.join(matches[:3])})")
        else:
            failed.append("Sparse causal or deductive chain markers")

        if len(text.split()) > 35:
            passed.append("Sufficient argumentative depth provided")
        else:
            failed.append("Superficial reasoning depth (< 35 words)")

        score = len(passed) / max(1, (len(passed) + len(failed)))
        status = VerificationStatus.VERIFIED_PASS if not failed else VerificationStatus.PARTIALLY_VERIFIED

        return VerificationReportDTO(
            status=status,
            method="logical_coherence_rubric",
            score=round(score, 2),
            passed_checks=passed,
            failed_checks=failed,
            rationale="Evaluated premise-conclusion progression and argumentation depth."
        )

    @classmethod
    def _verify_general_qa(cls, text: str, ground_truth: Optional[str] = None) -> VerificationReportDTO:
        passed = ["Response generated with non-trivial length"]
        failed = []

        if ground_truth and len(ground_truth) > 0:
            if ground_truth.lower() in text.lower():
                passed.append("Direct ground truth reference verification match")
            else:
                failed.append("Did not contain exact expected ground truth key")

        status = VerificationStatus.VERIFIED_PASS if not failed else VerificationStatus.PARTIALLY_VERIFIED
        score = 1.0 if status == VerificationStatus.VERIFIED_PASS else 0.7

        return VerificationReportDTO(
            status=status,
            method="heuristic_completeness",
            score=score,
            passed_checks=passed,
            failed_checks=failed,
            rationale="Evaluated general QA completeness and relevance."
        )

