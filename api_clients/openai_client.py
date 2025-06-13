import openai
from .llm_client import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def get_move(self, messages, model_name):
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except openai.NotFoundError:
            return "MODEL_NOT_FOUND"
        except Exception as e:
            print(f"Error communicating with OpenAI: {e}")
            return None
