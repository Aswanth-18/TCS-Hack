from app.core.config import settings
from app.services.provider_adapters.base import BaseProviderAdapter
from app.services.provider_adapters.simulator import SimulatorAdapter
from app.services.provider_adapters.real_adapters import OpenAIAdapter, GroqAdapter, GeminiAdapter

class ProviderAdapterFactory:
    """
    Adapter Factory: returns real provider adapter if valid API keys exist;
    seamlessly falls back to SimulatorAdapter with is_simulated=True otherwise.
    """

    @classmethod
    def get_adapter(cls, provider: str) -> BaseProviderAdapter:
        p = provider.lower()
        if p == "openai" and settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 10:
            return OpenAIAdapter(api_key=settings.OPENAI_API_KEY)
        elif p == "groq" and settings.GROQ_API_KEY and len(settings.GROQ_API_KEY) > 10:
            return GroqAdapter(api_key=settings.GROQ_API_KEY)
        elif (p == "google" or p == "gemini") and settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10:
            return GeminiAdapter(api_key=settings.GEMINI_API_KEY)
        else:
            return SimulatorAdapter(provider_name=provider)

