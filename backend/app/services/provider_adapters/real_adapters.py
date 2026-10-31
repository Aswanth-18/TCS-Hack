import httpx
import time
from typing import Optional
from app.services.provider_adapters.base import BaseProviderAdapter, AdapterExecutionResult

class OpenAIAdapter(BaseProviderAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def execute(
        self,
        prompt: str,
        model_id: str,
        max_tokens: int = 1500,
        temperature: float = 0.2,
        simulate_failure: bool = False
    ) -> AdapterExecutionResult:
        start_time = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)

                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    in_tok = usage.get("prompt_tokens", len(prompt.split()) * 2)
                    out_tok = usage.get("completion_tokens", len(content.split()) * 2)

                    return AdapterExecutionResult(
                        model_id=model_id,
                        provider="openai",
                        response_text=content,
                        input_tokens=in_tok,
                        output_tokens=out_tok,
                        total_tokens=in_tok + out_tok,
                        latency_ms=elapsed_ms,
                        status="success",
                        is_simulated=False,
                        provider_request_id=data.get("id")
                    )
                else:
                    return AdapterExecutionResult(
                        model_id=model_id,
                        provider="openai",
                        response_text="",
                        input_tokens=len(prompt.split()) * 2,
                        output_tokens=0,
                        total_tokens=len(prompt.split()) * 2,
                        latency_ms=elapsed_ms,
                        status="error",
                        error_message=f"OpenAI API Error ({res.status_code}): {res.text[:200]}",
                        is_simulated=False
                    )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return AdapterExecutionResult(
                model_id=model_id,
                provider="openai",
                response_text="",
                input_tokens=len(prompt.split()) * 2,
                output_tokens=0,
                total_tokens=len(prompt.split()) * 2,
                latency_ms=elapsed_ms,
                status="timeout" if "timeout" in str(e).lower() else "error",
                error_message=str(e),
                is_simulated=False
            )


class GroqAdapter(BaseProviderAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def execute(
        self,
        prompt: str,
        model_id: str,
        max_tokens: int = 1500,
        temperature: float = 0.2,
        simulate_failure: bool = False
    ) -> AdapterExecutionResult:
        start_time = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)

                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    in_tok = usage.get("prompt_tokens", len(prompt.split()) * 2)
                    out_tok = usage.get("completion_tokens", len(content.split()) * 2)

                    return AdapterExecutionResult(
                        model_id=model_id,
                        provider="groq",
                        response_text=content,
                        input_tokens=in_tok,
                        output_tokens=out_tok,
                        total_tokens=in_tok + out_tok,
                        latency_ms=elapsed_ms,
                        status="success",
                        is_simulated=False,
                        provider_request_id=data.get("id")
                    )
                else:
                    return AdapterExecutionResult(
                        model_id=model_id,
                        provider="groq",
                        response_text="",
                        input_tokens=len(prompt.split()) * 2,
                        output_tokens=0,
                        total_tokens=len(prompt.split()) * 2,
                        latency_ms=elapsed_ms,
                        status="error",
                        error_message=f"Groq API Error ({res.status_code}): {res.text[:200]}",
                        is_simulated=False
                    )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return AdapterExecutionResult(
                model_id=model_id,
                provider="groq",
                response_text="",
                input_tokens=len(prompt.split()) * 2,
                output_tokens=0,
                total_tokens=len(prompt.split()) * 2,
                latency_ms=elapsed_ms,
                status="error",
                error_message=str(e),
                is_simulated=False
            )


class GeminiAdapter(BaseProviderAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def execute(
        self,
        prompt: str,
        model_id: str,
        max_tokens: int = 1500,
        temperature: float = 0.2,
        simulate_failure: bool = False
    ) -> AdapterExecutionResult:
        start_time = time.perf_counter()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(url, json=payload)
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)

                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    content = candidates[0]["content"]["parts"][0]["text"] if candidates else ""
                    metadata = data.get("usageMetadata", {})
                    in_tok = metadata.get("promptTokenCount", len(prompt.split()) * 2)
                    out_tok = metadata.get("candidatesTokenCount", len(content.split()) * 2)

                    return AdapterExecutionResult(
                        model_id=model_id,
                        provider="google",
                        response_text=content,
                        input_tokens=in_tok,
                        output_tokens=out_tok,
                        total_tokens=in_tok + out_tok,
                        latency_ms=elapsed_ms,
                        status="success",
                        is_simulated=False
                    )
                else:
                    return AdapterExecutionResult(
                        model_id=model_id,
                        provider="google",
                        response_text="",
                        input_tokens=len(prompt.split()) * 2,
                        output_tokens=0,
                        total_tokens=len(prompt.split()) * 2,
                        latency_ms=elapsed_ms,
                        status="error",
                        error_message=f"Gemini API Error ({res.status_code}): {res.text[:200]}",
                        is_simulated=False
                    )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return AdapterExecutionResult(
                model_id=model_id,
                provider="google",
                response_text="",
                input_tokens=len(prompt.split()) * 2,
                output_tokens=0,
                total_tokens=len(prompt.split()) * 2,
                latency_ms=elapsed_ms,
                status="error",
                error_message=str(e),
                is_simulated=False
            )

