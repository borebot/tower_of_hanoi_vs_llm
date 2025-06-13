import requests
import json
from .llm_client import LLMClient
from config.settings import settings

class OllamaClient(LLMClient):
    def __init__(self, api_url=None):
        self.base_url = api_url or settings.OLLAMA_API_URL
        if not self.base_url:
            raise ValueError("Ollama API URL not provided or found in settings.")
        self.chat_url = f"{self.base_url}/api/chat"
        self.tags_url = f"{self.base_url}/api/tags"

    def get_models(self):
        try:
            response = requests.get(self.tags_url)
            response.raise_for_status()
            return response.json()["models"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Ollama models: {e}")
            return []

    def get_move(self, messages, model_name):
        try:
            response = requests.post(
                self.chat_url,
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False,
                },
            )
            response.raise_for_status()
            response_data = response.json()
            return response_data["message"]["content"]
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 404:
                return "MODEL_NOT_FOUND"
            print(f"Error communicating with Ollama: {e}")
            return None
