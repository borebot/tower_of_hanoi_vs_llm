import google.generativeai as genai
from .llm_client import LLMClient

class GeminiClient(LLMClient):
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.client = None

    def get_move(self, messages, model_name):
        self.client = genai.GenerativeModel(model_name)
        
        # Create a copy of the messages to avoid modifying the original list
        messages = list(messages)

        # The Gemini API uses a different format ("contents") and roles ("user", "model").
        system_prompt = ""
        
        # Find and extract the system prompt, then remove it from the list
        if messages and messages[0]['role'] == 'system':
            system_prompt = messages.pop(0)['content']

        # Find the first user message and prepend the system prompt
        if system_prompt:
            for message in messages:
                if message['role'] == 'user':
                    message['content'] = system_prompt + "\n\n" + message['content']
                    break # Stop after prepending to the first user message

        # Convert the rest of the messages to the Gemini format
        contents = []
        for message in messages:
            role = "model" if message["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": message["content"]}]})

        try:
            response = self.client.generate_content(contents=contents)
            return response.text
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                return "MODEL_NOT_FOUND"
            print(f"Error communicating with Gemini: {e}")
            return None
