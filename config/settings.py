import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        # --- Game Settings ---
        # The default number of stones to use in the game. This can be overridden in the UI.
        self.NUM_STONES = int(os.getenv("NUM_STONES", 3))
        # The maximum number of moves the LLM can make before the game automatically ends.
        self.MAX_MOVES = int(os.getenv("MAX_MOVES", 200))

        # --- LLM Settings ---
        # The default LLM provider to use (e.g., "ollama", "gemini").
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
        # The default LLM model to use.
        self.LLM_MODEL = os.getenv("LLM_MODEL")
        # The URL for the Ollama API server.
        self.OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
        # API keys for the different cloud providers.
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        # --- UI Settings ---
        # This setting is not currently implemented.
        self.STREAMING_RESPONSE = os.getenv("STREAMING_RESPONSE", "False").lower() in ('true', '1', 't')
        # The network port the Flask web server will run on.
        self.FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT", 5000)

        # --- Logging ---
        # The directory where game logs will be saved.
        self.LOGS_DIR = os.getenv("LOGS_DIR", "logs")

        # --- Prompts ---
        # Loads the system and user prompts from the prompts.json file.
        self.PROMPTS = self._load_prompts()

    @property
    def API_KEY(self):
        """A property that returns the correct API key based on the selected LLM_PROVIDER."""
        if self.LLM_PROVIDER == "gemini":
            return self.GEMINI_API_KEY
        elif self.LLM_PROVIDER == "claude":
            return self.CLAUDE_API_KEY
        elif self.LLM_PROVIDER == "openai":
            return self.OPENAI_API_KEY
        return None

    def _load_prompts(self):
        """Loads the prompts from the prompts.json file."""
        try:
            with open("config/prompts.json", "r") as f:
                prompts = json.load(f)
                # Remove the _comment fields from the loaded prompts so they aren't sent to the LLM
                if "_comment" in prompts:
                    del prompts["_comment"]
                if "user_prompts" in prompts and "_comment" in prompts["user_prompts"]:
                    del prompts["user_prompts"]["_comment"]
                return prompts
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading prompts.json: {e}")
            return {}

settings = Settings()
