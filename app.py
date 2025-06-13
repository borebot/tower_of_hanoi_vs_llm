import json
import logging
import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from game import HanoiGame
from llm_interface import LLMInterface
from config.settings import settings


app = Flask(__name__)
socketio = SocketIO(app)

game = HanoiGame(num_stones=settings.NUM_STONES, max_moves=settings.MAX_MOVES)
llm_interface = None
game_active = False
game_paused = False
chat_history = []
user_override_message = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/models/<provider>')
def get_models(provider):
    if provider == 'ollama':
        from api_clients.ollama_client import OllamaClient
        client = OllamaClient(settings.OLLAMA_API_URL)
        models = client.get_models()
        # The format from Ollama is a list of objects, we need a list of strings
        model_names = [model['name'] for model in models]
        return json.dumps({'models': model_names})
    return send_from_directory('config', f'{provider}_models.json')

@socketio.on('connect')
def handle_connect():
    emit('game_state', game.get_state(game_active, game_paused))

@socketio.on('start_game')
def handle_start_game(data):
    global game, game_active, game_paused, llm_interface, chat_history
    provider = data.get('provider')
    model_name = data.get('model_name')
    num_stones = data.get('num_stones', settings.NUM_STONES)

    if not provider:
        emit('chat_message', {'sender': 'system', 'message': 'Error: LLM Provider is required.'})
        return
    if not model_name:
        emit('chat_message', {'sender': 'system', 'message': 'Error: Model name is required.'})
        return

    # Re-initialize the LLM interface with the selected provider and model
    try:
        llm_interface = LLMInterface(provider=provider, api_key=settings.API_KEY, model_name=model_name)
    except ValueError as e:
        emit('chat_message', {'sender': 'system', 'message': f"Error: {e}"})
        return

    if not game_active:
        game = HanoiGame(num_stones=num_stones, max_moves=settings.MAX_MOVES) # Re-initialize the game
        chat_history = [] # Reset history on new game
        system_prompt = settings.PROMPTS.get("system_prompt", "")
        chat_history.append({"role": "system", "content": system_prompt})
        game_active = True
        game_paused = False
        socketio.start_background_task(run_game_loop)

@socketio.on('pause_game')
def handle_pause_game():
    global game_paused
    game_paused = True
    emit('game_state', game.get_state(game_active, game_paused))
    emit('chat_message', {'sender': 'system', 'message': 'Game paused.'})

@socketio.on('resume_game')
def handle_resume_game():
    global game_paused
    game_paused = False
    emit('game_state', game.get_state(game_active, game_paused))
    emit('chat_message', {'sender': 'system', 'message': 'Game resumed.'})

def log_game_session(ending_reason: str):
    """Logs the final chat history to a file."""
    if not llm_interface or not llm_interface.provider or not llm_interface.model_name:
        print("Could not log game session: LLM interface not fully initialized.")
        return

    log_dir = "game_logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    provider = llm_interface.provider
    model_name = llm_interface.model_name.replace('/', '_').replace(':', '_') # Sanitize model name for filename
    filename = f"{provider}_{model_name}_{timestamp}_{ending_reason}.log"
    filepath = os.path.join(log_dir, filename)

    try:
        with open(filepath, "w") as f:
            json.dump(chat_history, f, indent=2)
        print(f"Game session logged to {filepath}")
    except Exception as e:
        print(f"Error logging game session to {filepath}: {e}")


@socketio.on('end_game')
def handle_end_game():
    global game_active
    if game_active:
        log_game_session("ended")
    game_active = False

@socketio.on('reset_game')
def handle_reset_game():
    global game_active, game_paused, chat_history
    if game_active:
        log_game_session("reset")
    game.reset()
    chat_history = []
    game_active = False
    game_paused = False
    emit('clear_chat') # Clear the UI's chat log
    emit('game_state', game.get_state(game_active, game_paused))
    emit('chat_message', {'sender': 'system', 'message': 'Game has been reset.'})

@socketio.on('send_user_message')
def handle_send_user_message(data):
    global user_override_message
    if game_paused:
        user_override_message = data['message']
        handle_resume_game()


def run_game_loop():
    global game_active, game_paused, llm_interface, chat_history, user_override_message
    if not llm_interface:
        socketio.emit('chat_message', {'sender': 'system', 'message': 'LLM not initialized. Please start the game.'})
        return

    # Create the initial user prompt
    user_prompt = settings.PROMPTS["user_prompts"]["initial_state"].format(initial_game_state=game.to_llm_json())

    while game_active:
        if game_paused:
            socketio.sleep(1)
            continue

        if game.check_win():
            socketio.emit('chat_message', {'sender': 'system', 'message': f"Congratulations! You won in {game.moves} moves."})
            log_game_session("win")
            game_active = False
            break

        if game.is_out_of_moves():
            socketio.emit('chat_message', {'sender': 'system', 'message': f"Game over! Exceeded maximum moves ({game.max_moves})."})
            log_game_session("oom")
            game_active = False
            break
        
        is_custom_message = False
        if user_override_message:
            user_prompt = user_override_message
            user_override_message = None # Reset after use
            is_custom_message = True

        # 1. Send the current prompt to the UI and add it to history
        sender = 'user' if is_custom_message else 'game'
        socketio.emit('chat_message', {'sender': sender, 'message': user_prompt})
        chat_history.append({"role": "user", "content": user_prompt})

        # 2. Get the LLM's move
        move, llm_response = llm_interface.get_llm_move(chat_history)

        # 3. Handle LLM response (or lack thereof)
        if llm_response == "MODEL_NOT_FOUND":
            socketio.emit('chat_message', {'sender': 'system', 'message': f"Error: Model '{llm_interface.model_name}' not found."})
            game_active = False
            break
        
        if llm_response:
            socketio.emit('chat_message', {'sender': 'llm', 'message': llm_response})
            chat_history.append({"role": "assistant", "content": llm_response})
        else:
            socketio.emit('chat_message', {'sender': 'system', 'message': "LLM failed to provide a response."})
            game_active = False
            break

        # 4. Process the move and prepare the NEXT user_prompt
        if is_custom_message:
             user_prompt = settings.PROMPTS["user_prompts"]["move_success"].format(game_state_string=game.to_llm_json())
        elif move:
            from_cairn, to_cairn = move
            if game.move_stone(from_cairn, to_cairn):
                socketio.emit('game_state', game.get_state(game_active, game_paused))
                result_message = f"Move successful. New moves count: {game.moves}"
                socketio.emit('chat_message', {'sender': 'system', 'message': result_message})
                user_prompt = settings.PROMPTS["user_prompts"]["move_success"].format(game_state_string=game.to_llm_json())
            else:
                result_message = "LLM suggested an invalid move."
                socketio.emit('chat_message', {'sender': 'system', 'message': result_message})
                user_prompt = settings.PROMPTS["user_prompts"]["invalid_move"].format(game_state_string=game.to_llm_json())
        else:
            result_message = "LLM failed to provide a valid move in the correct format."
            socketio.emit('chat_message', {'sender': 'system', 'message': result_message})
            user_prompt = settings.PROMPTS["user_prompts"]["invalid_move_format"].format(game_state_string=game.to_llm_json())

        socketio.sleep(2)

if __name__ == '__main__':
    socketio.run(app, debug=True)
