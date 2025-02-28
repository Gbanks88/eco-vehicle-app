// Connect to Socket.IO server
const socket = io('http://localhost:3000');

class MotherboardGame {
    static GAME_STATES = {
        MENU: 'menu',
        PLAYING: 'playing',
        MULTIPLAYER: 'multiplayer',
        GAME_OVER: 'game_over'
    };
    constructor() {
        this.gameState = MotherboardGame.GAME_STATES.MENU;
        this.playerName = '';
        this.activePlayers = [];
        this.achievements = [];
        this.setupSocketListeners();
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({
            canvas: document.getElementById('game-canvas'),
            antialias: true
        });
        this.score = 0;
        this.level = 1;
        this.timeRemaining = 60;
        this.components = [];
        this.componentData = {
            cpuSocket: {
                name: 'CPU Socket',
                description: 'The CPU socket is where the processor is installed. It contains many pins that connect the CPU to the rest of the system.',
                position: { x: 0, y: 0, z: 0 },
                color: 0x666666
            },
            ramSlots: {
                name: 'RAM Slots',
                description: 'These slots hold the memory modules (RAM) that provide temporary storage for active programs and data.',
                position: { x: 2, y: 0, z: 0 },
                color: 0x333333
            },
            pciSlots: {
                name: 'PCIe Slots',
                description: 'Expansion slots for adding graphics cards, sound cards, and other peripherals.',
                position: { x: -2, y: 0, z: 0 },
                color: 0x222222
            },
            // Add more components here
        };

        this.init();
    }

    setupSocketListeners() {
        socket.on('playerJoined', (playerName) => {
            this.showNotification(`${playerName} joined the game`);
            this.updatePlayersList();
        });

        socket.on('playerLeft', (playerName) => {
            this.showNotification(`${playerName} left the game`);
            this.updatePlayersList();
        });

        socket.on('activePlayers', (players) => {
            this.activePlayers = players;
            this.updatePlayersList();
        });

        socket.on('chatMessage', (data) => {
            this.showChatMessage(data);
        });

        socket.on('newChallenge', (data) => {
            if (data.targetPlayer === this.playerName) {
                this.showChallenge(data.challenger);
            }
        });

        socket.on('achievementsUnlocked', (achievements) => {
            achievements.forEach(achievement => {
                this.showAchievementUnlocked(achievement);
            });
        });
    }

    init() {
        this.setupRenderer();
        this.setupCamera();
        this.setupLights();
        this.createMotherboard();
        this.setupEventListeners();
        this.animate();
        this.startTimer();
    }

    setupRenderer() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x1a1a1a);
    }

    setupCamera() {
        this.camera.position.z = 10;
        this.camera.position.y = 5;
        this.camera.lookAt(0, 0, 0);
    }

    setupLights() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);
    }

    createMotherboard() {
        // Create base motherboard
        const boardGeometry = new THREE.BoxGeometry(10, 0.2, 8);
        const boardMaterial = new THREE.MeshPhongMaterial({ color: 0x006600 });
        this.motherboard = new THREE.Mesh(boardGeometry, boardMaterial);
        this.scene.add(this.motherboard);

        // Add components
        Object.entries(this.componentData).forEach(([key, data]) => {
            this.createComponent(key, data);
        });
    }

    createComponent(key, data) {
        const geometry = new THREE.BoxGeometry(1, 0.3, 1);
        const material = new THREE.MeshPhongMaterial({ 
            color: data.color,
            emissive: data.color,
            emissiveIntensity: 0.2
        });
        const component = new THREE.Mesh(geometry, material);
        
        component.position.set(
            data.position.x,
            0.25,
            data.position.z
        );
        
        component.userData = {
            type: key,
            name: data.name,
            description: data.description
        };
        
        this.motherboard.add(component);
        this.components.push(component);
    }

    setupEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
        
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, this.camera);
            const intersects = raycaster.intersectObjects(this.components);

            if (intersects.length > 0) {
                this.handleComponentClick(intersects[0].object);
            }
        });

        document.getElementById('start-game').addEventListener('click', () => {
            document.getElementById('tutorial').classList.add('hidden');
            this.startGame();
        });
    }

    handleComponentClick(component) {
        const data = component.userData;
        document.getElementById('component-description').textContent = data.description;
        this.showQuiz(data);
    }

    showQuiz(componentData) {
        const quizPanel = document.getElementById('quiz-panel');
        const question = this.generateQuestion(componentData);
        
        document.getElementById('quiz-question').textContent = question.text;
        const optionsContainer = document.getElementById('quiz-options');
        optionsContainer.innerHTML = '';
        
        question.options.forEach(option => {
            const button = document.createElement('div');
            button.className = 'quiz-option';
            button.textContent = option;
            button.addEventListener('click', () => this.checkAnswer(option, question.correct));
            optionsContainer.appendChild(button);
        });
        
        quizPanel.classList.remove('hidden');
    }

    generateQuestion(componentData) {
        // Simple question generation based on component data
        return {
            text: `What is the primary function of the ${componentData.name}?`,
            options: [
                componentData.description,
                'It controls the fan speed',
                'It stores permanent data',
                'It provides power to the USB ports'
            ],
            correct: componentData.description
        };
    }

    checkAnswer(selected, correct) {
        if (selected === correct) {
            this.score += 100;
            document.getElementById('score-value').textContent = this.score;
        }
        document.getElementById('quiz-panel').classList.add('hidden');
    }

    startTimer() {
        const timerElement = document.getElementById('timer-value');
        const timer = setInterval(() => {
            this.timeRemaining--;
            timerElement.textContent = this.timeRemaining;
            
            if (this.timeRemaining <= 0) {
                clearInterval(timer);
                this.endGame();
            }
        }, 1000);
    }

    endGame() {
        this.gameState = MotherboardGame.GAME_STATES.GAME_OVER;

        // Check for achievements
        socket.emit('checkAchievements', {
            score: this.score,
            timeLeft: this.timeRemaining
        });

        const playerName = this.playerName || prompt('Game Over! Enter your name for the high score:', 'Player');
        if (playerName) {
            this.playerName = playerName;
            socket.emit('newScore', {
                name: playerName,
                score: this.score,
                level: this.level
            });
        }
        this.showHighScores();
        const playerName = prompt('Game Over! Enter your name for the high score:', 'Player');
        if (playerName) {
            socket.emit('newScore', {
                name: playerName,
                score: this.score,
                level: this.level
            });
        }
        this.showHighScores();
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Add subtle motherboard rotation
        this.motherboard.rotation.y += 0.001;
        
        this.renderer.render(this.scene, this.camera);
    }

    showHighScores() {
        const highScoresDiv = document.createElement('div');
        highScoresDiv.className = 'overlay';
        highScoresDiv.innerHTML = `
            <div class='tutorial-content'>
                <h2>High Scores</h2>
                <div id='high-scores-list'></div>
                <button id='restart-game'>Play Again</button>
            </div>
        `;
        document.body.appendChild(highScoresDiv);

        document.getElementById('restart-game').addEventListener('click', () => {
            document.body.removeChild(highScoresDiv);
            location.reload();
        });
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    showChatMessage(data) {
        const chatBox = document.getElementById('chat-box');
        const message = document.createElement('div');
        message.className = 'chat-message';
        message.textContent = `${data.player}: ${data.message}`;
        chatBox.appendChild(message);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    showChallenge(challenger) {
        const challenge = document.createElement('div');
        challenge.className = 'challenge-popup';
        challenge.innerHTML = `
            <h3>${challenger} has challenged you!</h3>
            <button onclick="game.acceptChallenge('${challenger}')">Accept</button>
            <button onclick="this.parentElement.remove()">Decline</button>
        `;
        document.body.appendChild(challenge);
    }

    showAchievementUnlocked(achievement) {
        const popup = document.createElement('div');
        popup.className = 'achievement-popup';
        popup.innerHTML = `
            <h3>Achievement Unlocked!</h3>
            <p>${achievement}</p>
        `;
        document.body.appendChild(popup);
        setTimeout(() => popup.remove(), 5000);
    }

    updatePlayersList() {
        const playersList = document.getElementById('players-list');
        playersList.innerHTML = '';
        this.activePlayers.forEach(player => {
            if (player !== this.playerName) {
                const playerElement = document.createElement('div');
                playerElement.className = 'player-item';
                playerElement.innerHTML = `
                    ${player}
                    <button onclick="game.challengePlayer('${player}')">Challenge</button>
                `;
                playersList.appendChild(playerElement);
            }
        });
    }

    challengePlayer(targetPlayer) {
        socket.emit('challengePlayer', targetPlayer);
    }

    acceptChallenge(challenger) {
        this.gameState = MotherboardGame.GAME_STATES.MULTIPLAYER;
        // Start multiplayer game logic
    }

    startGame() {
        // Initialize game state
        this.score = 0;
        this.level = 1;
        document.getElementById('score-value').textContent = this.score;
        document.getElementById('level-value').textContent = this.level;
    }
}

// Start the game when the page loads
window.addEventListener('load', () => {
    const game = new MotherboardGame();
});
