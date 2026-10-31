from typing import Optional, List, Dict, Any

class CostCalculator:
    """
    Centralized FinOps Cost Calculation Service.
    Strictly calculates token costs per million, tracks multi-attempt costs,
    and computes Cost Per Successful Outcome (CPSO).
    """

    @staticmethod
    def calculate_token_cost(
        input_tokens: int,
        output_tokens: int,
        input_cost_per_m: float,
        output_cost_per_m: float
    ) -> float:
        """
        Calculates exact request cost in USD.
        Cost = (Input Tokens * Price per M / 1,000,000) + (Output Tokens * Price per M / 1,000,000)
        """
        input_cost = (input_tokens / 1_000_000.0) * input_cost_per_m
        output_cost = (output_tokens / 1_000_000.0) * output_cost_per_m
        return round(input_cost + output_cost, 6)

    @staticmethod
    def calculate_cost_per_successful_outcome(
        total_cost_all_attempts: float,
        verified_success_count: int
    ) -> Optional[float]:
        """
        Calculates Cost Per Successful Outcome (CPSO):
        CPSO = Total cost of all attempts in evaluation scope / Number of verified successful outcomes.
        If verified successes == 0, returns None (displayed as undefined/unavailable).
        """
        if verified_success_count <= 0:
            return None
        return round(total_cost_all_attempts / float(verified_success_count), 6)

    @staticmethod
    def estimate_tokens_from_prompt(prompt: str, task_type: str = "general_qa") -> Dict[str, int]:
        """
        Heuristic / measured token estimation:
        ~1 token ~= 4 characters for English text.
        Output tokens estimated by task type expected generation length.
        """
        char_count = len(prompt.strip())
        input_tokens = max(1, int(char_count / 3.8))

        # Expected output expansion multiplier based on task category
        multiplier_map = {
            "coding": 2.5,
            "reasoning": 2.0,
            "data_analysis": 1.8,
            "summarization": 0.6,
            "structured_output": 1.5,
            "general_qa": 1.2
        }
        multiplier = multiplier_map.get(task_type, 1.2)
        output_tokens = max(60, min(1500, int(input_tokens * multiplier)))

        return {
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_total_tokens": input_tokens + output_tokens
        }

