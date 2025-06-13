import re
from api_clients.llm_client import LLMClientFactory

class LLMInterface:
    def __init__(self, provider, api_key=None, model_name=None):
        self.provider = provider
        self.client = LLMClientFactory.create_client(provider, api_key)
        self.model_name = model_name

    def get_llm_move(self, history):
        # This function now simply passes the history to the client
        response = self.client.get_move(history, self.model_name)
        
        if response:
            return self.parse_move(response), response
        
        return None, None

    def parse_move(self, response):
        # This regex now looks for the move pattern at the very end of the string,
        # ignoring case and allowing for trailing whitespace.
        match = re.search(r"([A-C])\s+to\s+([A-C])\s*$", response, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).upper(), match.group(2).upper()
        return None
