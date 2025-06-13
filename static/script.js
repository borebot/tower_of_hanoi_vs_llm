document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resumeBtn = document.getElementById('resume-btn');
    const endBtn = document.getElementById('end-btn');
    const resetBtn = document.getElementById('reset-btn');
    const sendBtn = document.getElementById('send-btn');
    const messageInput = document.getElementById('message-input');
    const visualization = document.getElementById('visualization');
    const chatLog = document.getElementById('chat-log');
    const llmProviderSelect = document.getElementById('llm-provider');
    const modelNameInput = document.getElementById('model-name');
    const modelSelect = document.getElementById('model-select');
    const manualModelToggle = document.getElementById('manual-model-toggle');
    const numStonesInput = document.getElementById('num-stones');

    async function fetchModels(provider) {
        manualModelToggle.disabled = false;
        if (provider === 'ollama') {
            manualModelToggle.checked = false;
        }


        try {
            const response = await fetch(`/models/${provider}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            modelSelect.innerHTML = '';
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            modelSelect.style.display = 'block';
            modelNameInput.style.display = 'none';
            manualModelToggle.checked = false;
        } catch (error) {
            console.error('Could not fetch models:', error);
            modelSelect.style.display = 'none';
            modelNameInput.style.display = 'block';
            manualModelToggle.checked = true;
        }
    }

    llmProviderSelect.addEventListener('change', () => {
        fetchModels(llmProviderSelect.value);
    });

    manualModelToggle.addEventListener('change', () => {
        if (manualModelToggle.checked) {
            modelSelect.style.display = 'none';
            modelNameInput.style.display = 'block';
        } else {
            modelSelect.style.display = 'block';
            modelNameInput.style.display = 'none';
        }
    });

    startBtn.addEventListener('click', () => {
        const provider = llmProviderSelect.value;
        const modelName = manualModelToggle.checked ? modelNameInput.value : modelSelect.value;
        const numStones = parseInt(numStonesInput.value, 10);
        socket.emit('start_game', { provider, model_name: modelName, num_stones: numStones });
    });
    pauseBtn.addEventListener('click', () => socket.emit('pause_game'));
    resumeBtn.addEventListener('click', () => socket.emit('resume_game'));
    endBtn.addEventListener('click', () => socket.emit('end_game'));
    resetBtn.addEventListener('click', () => socket.emit('reset_game'));
    function sendMessage() {
        if (messageInput.value.trim()) {
            socket.emit('send_user_message', { message: messageInput.value });
            messageInput.value = '';
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevents the default form submission
            sendMessage();
        }
    });

    socket.on('game_state', (data) => {
        updateVisualization(data.cairns);
        updateButtonStates(data);
    });

    socket.on('clear_chat', () => {
        chatLog.innerHTML = '';
    });

    socket.on('chat_message', (data) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', data.sender);

        const jsonRegex = /^(.*?)\s*({.*})\s*(.*)$/s; // Regex to find text, JSON, and more text
        const match = data.message.match(jsonRegex);

        if (match) {
            const beforeText = match[1].trim();
            const jsonPart = match[2];
            const afterText = match[3].trim();

            if (beforeText) {
                const beforeNode = document.createElement('div');
                beforeNode.innerText = beforeText;
                messageElement.appendChild(beforeNode);
            }

            const preElement = document.createElement('pre');
            preElement.textContent = jsonPart;
            messageElement.appendChild(preElement);

            if (afterText) {
                const afterNode = document.createElement('div');
                afterNode.innerText = afterText;
                messageElement.appendChild(afterNode);
            }
        } else {
            // No JSON found, just display the plain text
            messageElement.innerText = data.message;
        }

        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    });

    function updateVisualization(cairns) {
        visualization.innerHTML = '';
        for (const cairnName in cairns) {
            const cairnElement = document.createElement('div');
            cairnElement.classList.add('cairn');
            cairnElement.dataset.cairn = cairnName;

            const nameElement = document.createElement('div');
            nameElement.classList.add('cairn-name');
            nameElement.textContent = cairnName;
            cairnElement.appendChild(nameElement);

            const stones = cairns[cairnName];
            for (let i = 0; i < stones.length; i++) {
                const stoneElement = document.createElement('div');
                stoneElement.classList.add('stone');
                stoneElement.style.width = `${stones[i] * 12 + 20}px`;
                stoneElement.textContent = stones[i];
                cairnElement.appendChild(stoneElement);
            }
            visualization.appendChild(cairnElement);
        }
    }

    function updateButtonStates(data) {
        startBtn.disabled = data.is_active;
        pauseBtn.disabled = !data.is_active || data.is_paused;
        resumeBtn.disabled = !data.is_active || !data.is_paused;
        endBtn.disabled = !data.is_active;
        messageInput.disabled = !data.is_paused;
        sendBtn.disabled = !data.is_paused;
    }

    function initializeVisualization(numStones) {
        const cairns = {
            'A': Array.from({ length: numStones }, (_, i) => numStones - i),
            'B': [],
            'C': []
        };
        updateVisualization(cairns);
    }

    numStonesInput.addEventListener('input', () => {
        const numStones = parseInt(numStonesInput.value, 10);
        // Basic validation to match the input's min/max
        if (!isNaN(numStones) && numStones >= 2 && numStones <= 10) {
            initializeVisualization(numStones);
        }
    });

    // Initial visualization on page load
    initializeVisualization(parseInt(numStonesInput.value, 10));
    // Fetch models for the default provider
    fetchModels(llmProviderSelect.value);
});
