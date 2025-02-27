const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Enable CORS
app.use(cors());

// Serve static files
app.use(express.static(__dirname));

// SQLite setup
const db = new sqlite3.Database(path.join(__dirname, 'game.db'), (err) => {
    if (err) {
        console.error('Error opening database:', err);
    } else {
        console.log('Connected to SQLite database');
        initializeDatabase();
    }
});

// Initialize database tables
function initializeDatabase() {
    db.serialize(() => {
        // Create players table
        db.run(`CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            score INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            last_played DATETIME
        )`);

        // Create achievements table
        db.run(`CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            points INTEGER
        )`);

        // Create player_achievements table
        db.run(`CREATE TABLE IF NOT EXISTS player_achievements (
            player_id INTEGER,
            achievement_id INTEGER,
            unlocked_at DATETIME,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(achievement_id) REFERENCES achievements(id),
            PRIMARY KEY(player_id, achievement_id)
        )`);

        // Insert default achievements
        const achievements = [
            ['First Steps', 'Complete your first game', 10],
            ['Expert', 'Score over 1000 points', 50],
            ['Speed Demon', 'Complete a game in under 30 seconds', 30]
        ];

        const stmt = db.prepare('INSERT OR IGNORE INTO achievements (name, description, points) VALUES (?, ?, ?)');
        achievements.forEach(achievement => stmt.run(achievement));
        stmt.finalize();
    });
}

// Active rooms and players
const gameRooms = new Map();
let activeUsers = new Map();

// Socket.IO connection handling
// Handle achievements
function checkAndAwardAchievements(socket, playerName, data) {
    db.get('SELECT id FROM players WHERE name = ?', [playerName], (err, player) => {
        if (err || !player) return;

        // Check each achievement condition
        if (data.score > 1000) {
            awardAchievement(player.id, 'Expert', socket);
        }
        if (data.timeLeft > 30) {
            awardAchievement(player.id, 'Speed Demon', socket);
        }
    });
}

function awardAchievement(playerId, achievementName, socket) {
    db.get('SELECT id FROM achievements WHERE name = ?', [achievementName], (err, achievement) => {
        if (err || !achievement) return;

        db.run(
            'INSERT OR IGNORE INTO player_achievements (player_id, achievement_id, unlocked_at) VALUES (?, ?, datetime("now"))',
            [playerId, achievement.id],
            (err) => {
                if (!err) {
                    socket.emit('achievementUnlocked', achievementName);
                }
            }
        );
    });
}

io.on('connection', (socket) => {
    console.log('A user connected');
    
    // Handle player join
    socket.on('joinGame', (playerName) => {
        activeUsers.set(socket.id, playerName);
        
        // Create or update player in database
        db.run(
            `INSERT OR REPLACE INTO players (name, games_played, last_played) 
             VALUES (?, COALESCE((SELECT games_played + 1 FROM players WHERE name = ?), 1), datetime('now'))`,
            [playerName, playerName]
        );

        // Notify others
        socket.broadcast.emit('playerJoined', playerName);
        
        // Send active players list
        io.emit('activePlayers', Array.from(activeUsers.values()));
    });

    // Handle chat messages
    socket.on('chatMessage', (message) => {
        const playerName = activeUsers.get(socket.id);
        io.emit('chatMessage', { player: playerName, message });
    });

    // Handle multiplayer challenges
    socket.on('challengePlayer', (targetPlayer) => {
        const challenger = activeUsers.get(socket.id);
        io.emit('newChallenge', { challenger, targetPlayer });
    });

    // Handle achievement checks
    socket.on('checkAchievements', (data) => {
        const playerName = activeUsers.get(socket.id);
        if (playerName) {
            checkAndAwardAchievements(socket, playerName, data);
        }
    });

    // Send current high scores to new connections
    db.all('SELECT name, score FROM players ORDER BY score DESC LIMIT 10', [], (err, rows) => {
        if (!err) {
            socket.emit('highScores', rows);
        }
    });

    // Handle new scores
    socket.on('newScore', (data) => {
        db.run('INSERT OR REPLACE INTO players (name, score) VALUES (?, ?)',
            [data.name, data.score],
            (err) => {
                if (!err) {
                    // Fetch and broadcast updated high scores
                    db.all('SELECT name, score FROM players ORDER BY score DESC LIMIT 10',
                        [],
                        (err, rows) => {
                            if (!err) {
                                io.emit('highScores', rows);
                            }
                        });
                }
            });
    });

    socket.on('disconnect', () => {
        const playerName = activeUsers.get(socket.id);
        activeUsers.delete(socket.id);
        io.emit('playerLeft', playerName);
        io.emit('activePlayers', Array.from(activeUsers.values()));
        console.log('User disconnected:', playerName);
    });
});

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
