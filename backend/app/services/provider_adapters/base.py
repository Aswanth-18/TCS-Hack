from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, Dict, Any

class AdapterExecutionResult(BaseModel):
    model_id: str
    provider: str
    response_text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    status: str # "success", "timeout", "rate_limit", "error"
    error_message: Optional[str] = None
    is_simulated: bool = False
    provider_request_id: Optional[str] = None
    raw_metadata: Dict[str, Any] = {}

class BaseProviderAdapter(ABC):
    @abstractmethod
    async def execute(
        self,
        prompt: str,
        model_id: str,
        max_tokens: int = 1500,
        temperature: float = 0.2,
        simulate_failure: bool = False
    ) -> AdapterExecutionResult:
        pass

