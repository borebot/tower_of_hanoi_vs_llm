from abc import ABC, abstractmethod
from config.settings import settings

class LLMClient(ABC):
    @abstractmethod
    def get_move(self, messages, model_name):
        pass

class LLMClientFactory:
    @staticmethod
    def create_client(provider, api_key=None):
        if provider == "ollama":
            from .ollama_client import OllamaClient
            return OllamaClient(settings.OLLAMA_API_URL)
        elif provider == "gemini":
            from .gemini_client import GeminiClient
            return GeminiClient(api_key)
        elif provider == "anthropic":
            from .anthropic_client import AnthropicClient
            return AnthropicClient(api_key)
        elif provider == "openai":
            from .openai_client import OpenAIClient
            return OpenAIClient(api_key)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
