# Tower of Hanoi vs. LLM (Cairns and Stones)

This project is a web-based application that pits a Large Language Model (LLM) against the classic Tower of Hanoi puzzle. You can choose from different LLM providers (Ollama, Gemini, Anthropic, OpenAI) and models to see how they perform. The application provides a visual representation of the game and a chat interface to observe the LLM's reasoning process.

## Installation

These instructions will guide you through setting up and running the project on your local machine.

### 1. Clone the Repository

First, you need to clone this repository to your computer. Open your terminal or command prompt and run the following command:

```bash
git clone https://github.com/borebot/tower_of_hanoi_vs_llm.git
cd tower_of_hanoi_vs_llm
```

### 2. Set up a Virtual Environment

It's highly recommended to use a virtual environment to keep the project's dependencies separate from your system's Python installation.

**On macOS and Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

With your virtual environment activated, install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## How to Use

### 1. Configure Environment Variables

The project uses a `.env` file to manage secret keys and other settings.

1.  Find the file named `.env.example` in the main directory.
2.  Make a copy of this file and rename it to `.env`.
3.  Open the new `.env` file in a text editor and fill in the required values.

Here's a breakdown of the variables:

*   `LLM_PROVIDER`: This is set in the UI. (`ollama`, `gemini`, `claude`, or `openai`).
*   `LLM_MODEL`: Set this in the UI as well. The list should auto-populate for Ollama, and there are hardcoded lists of modesl for the cloud providers that you might have to edit if this repo is outdated.
*   `OLLAMA_API_URL`: If you are using Ollama, set the URL for your Ollama server (e.g., `http://localhost:11434`).
*   `GEMINI_API_KEY`, `CLAUDE_API_KEY`, `OPENAI_API_KEY`: Add your API keys for the respective services you want to use. You only need to fill in the key for the provider you are using.

### 2. Customize Prompts

You can change the prompts used to instruct the LLM by editing the `config/prompts.json` file.

*   `system_prompt`: This is the main instruction given to the LLM at the start of the game. It sets the rules and the expected output format.
*   `user_prompts`: These are the prompts sent to the LLM during the game to inform it of the current state or errors.

### 3. Understanding and Adjusting the Regex

The application parses the LLM's response to find a valid move using a regular expression (regex). This is crucial for the game to function correctly.

*   **Where to find it:** The regex is located in the `parse_move` method within the `llm_interface.py` file.
*   **How it works:** The current regex `([A-C])\s+to\s+([A-C])\s*$` is designed to find a move in the format "A to C" at the very end of the LLM's output. It's case-insensitive and allows for extra spaces.
*   **How to adjust it:** If you find that your chosen LLM provides moves in a different format, you may need to adjust this regex. For example, if the LLM outputs "Move from A to C", you might change the regex to something like `Move from ([A-C]) to ([A-C])`. The current system prompt tries to force a certain style of output, but YMMV.

### 4. Running the Application

Once you have everything configured, you can start the web server. Run the following command in your terminal (make sure your virtual environment is still active):

```bash
flask run
```

Then, open your web browser and go to `http://127.0.0.1:5000` (or the address shown in your terminal).

## Important Notes

*   **Provider Testing:** This application has been primarily tested with **Ollama** and **Gemini**. While support for OpenAI and Anthropic is included, the experience may vary. You might need to adjust the prompts or the regex for optimal performance with these providers.
*   **Model Performance:** The ability of the LLM to play the game correctly heavily depends on the model you choose. Some models may struggle to follow the rules or provide moves in the correct format.


## Usage Notes
At the end of a run, the full message payload (containing the back-and-forth) will be saved in game_logs. (The log ends at the last message the LLM sends back.)

The UI is equipped with a pause function if you feel the need to nudge the LLM in a certain direction. If you press pause, you can enter a message. Chances are the LLM will ignore the message if the system prompt is strong enough, but it really depends on the model.


Have fun!