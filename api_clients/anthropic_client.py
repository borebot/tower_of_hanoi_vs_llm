import anthropic
from .llm_client import LLMClient

class AnthropicClient(LLMClient):
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def get_move(self, messages, model_name):
        system_prompt = ""
        if messages and messages[0]['role'] == 'system':
            system_prompt = messages[0]['content']
            messages = messages[1:]

        try:
            response = self.client.messages.create(
                model=model_name,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except anthropic.NotFoundError:
            return "MODEL_NOT_FOUND"
        except Exception as e:
            print(f"Error communicating with Anthropic: {e}")
            return None
