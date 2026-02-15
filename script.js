class Tetris {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.nextCanvas = document.getElementById('nextCanvas');
        this.nextCtx = this.nextCanvas.getContext('2d');
        
        this.blockSize = 30;
        this.cols = 10;
        this.rows = 20;
        this.board = [];
        
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.dropTime = 1000;
        this.lastDrop = 0;
        
        this.currentPiece = null;
        this.nextPiece = null;
        this.gameOver = false;
        this.paused = false;
        this.gameStarted = false;
        
        this.colors = [
            '#00f0f0', // I - Cyan
            '#0000f0', // J - Blue
            '#f0a000', // L - Orange
            '#f0f000', // O - Yellow
            '#00f000', // S - Green
            '#a000f0', // T - Purple
            '#f00000'  // Z - Red
        ];
        
        this.pieces = [
            [[1,1,1,1]],           // I
            [[1,0,0],[1,1,1]],     // J
            [[0,0,1],[1,1,1]],     // L
            [[1,1],[1,1]],         // O
            [[0,1,1],[1,1,0]],     // S
            [[0,1,0],[1,1,1]],     // T
            [[1,1,0],[0,1,1]]      // Z
        ];
        
        this.init();
    }
    
    init() {
        this.setupBoard();
        this.setupEventListeners();
        this.updateDisplay();
    }
    
    setupBoard() {
        this.board = Array(this.rows).fill().map(() => Array(this.cols).fill(0));
    }
    
    setupEventListeners() {
        document.getElementById('startBtn').addEventListener('click', () => this.startGame());
        document.getElementById('pauseBtn').addEventListener('click', () => this.togglePause());
        
        document.addEventListener('keydown', (e) => {
            if (!this.gameStarted || this.gameOver) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.movePiece(-1, 0);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.movePiece(1, 0);
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.movePiece(0, 1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.rotatePiece();
                    break;
                case ' ':
                    e.preventDefault();
                    this.hardDrop();
                    break;
                case 'p':
                case 'P':
                    e.preventDefault();
                    this.togglePause();
                    break;
            }
        });
    }
    
    startGame() {
        this.gameStarted = true;
        this.gameOver = false;
        this.paused = false;
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.dropTime = 1000;
        this.setupBoard();
        this.spawnPiece();
        this.updateDisplay();
        document.getElementById('startBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        this.gameLoop();
    }
    
    togglePause() {
        if (!this.gameStarted || this.gameOver) return;
        this.paused = !this.paused;
        document.getElementById('pauseBtn').textContent = this.paused ? 'Resume' : 'Pause';
        if (!this.paused) {
            this.gameLoop();
        }
    }
    
    spawnPiece() {
        if (this.nextPiece === null) {
            this.nextPiece = this.createPiece();
        }
        this.currentPiece = this.nextPiece;
        this.nextPiece = this.createPiece();
        
        this.currentPiece.x = Math.floor((this.cols - this.currentPiece.shape[0].length) / 2);
        this.currentPiece.y = 0;
        
        if (this.collision()) {
            this.gameOver = true;
            this.gameStarted = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            alert('Game Over! Your score: ' + this.score);
        }
        
        this.drawNextPiece();
    }
    
    createPiece() {
        const typeId = Math.floor(Math.random() * this.pieces.length);
        return {
            shape: this.pieces[typeId],
            color: this.colors[typeId],
            x: 0,
            y: 0,
            type: typeId
        };
    }
    
    collision() {
        for (let y = 0; y < this.currentPiece.shape.length; y++) {
            for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                if (this.currentPiece.shape[y][x]) {
                    const boardX = this.currentPiece.x + x;
                    const boardY = this.currentPiece.y + y;
                    
                    if (boardX < 0 || boardX >= this.cols || 
                        boardY >= this.rows ||
                        (boardY >= 0 && this.board[boardY][boardX])) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    movePiece(dx, dy) {
        this.currentPiece.x += dx;
        this.currentPiece.y += dy;
        
        if (this.collision()) {
            this.currentPiece.x -= dx;
            this.currentPiece.y -= dy;
            
            if (dy > 0) {
                this.lockPiece();
                this.clearLines();
                this.spawnPiece();
            }
            return false;
        }
        return true;
    }
    
    rotatePiece() {
        const rotated = this.currentPiece.shape[0].map((_, index) =>
            this.currentPiece.shape.map(row => row[index]).reverse()
        );
        
        const previousShape = this.currentPiece.shape;
        this.currentPiece.shape = rotated;
        
        if (this.collision()) {
            this.currentPiece.shape = previousShape;
        }
    }
    
    hardDrop() {
        while (this.movePiece(0, 1)) {
            this.score += 2;
        }
        this.updateDisplay();
    }
    
    lockPiece() {
        for (let y = 0; y < this.currentPiece.shape.length; y++) {
            for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                if (this.currentPiece.shape[y][x]) {
                    const boardY = this.currentPiece.y + y;
                    const boardX = this.currentPiece.x + x;
                    if (boardY >= 0) {
                        this.board[boardY][boardX] = this.currentPiece.type + 1;
                    }
                }
            }
        }
    }
    
    clearLines() {
        let linesCleared = 0;
        
        for (let y = this.rows - 1; y >= 0; y--) {
            if (this.board[y].every(cell => cell !== 0)) {
                this.board.splice(y, 1);
                this.board.unshift(Array(this.cols).fill(0));
                linesCleared++;
                y++;
            }
        }
        
        if (linesCleared > 0) {
            this.lines += linesCleared;
            this.score += [40, 100, 300, 1200][linesCleared - 1] * this.level;
            
            const newLevel = Math.floor(this.lines / 10) + 1;
            if (newLevel > this.level) {
                this.level = newLevel;
                this.dropTime = Math.max(100, 1000 - (this.level - 1) * 100);
            }
            
            this.updateDisplay();
        }
    }
    
    draw() {
        this.ctx.fillStyle = '#111';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.drawBoard();
        this.drawCurrentPiece();
    }
    
    drawBoard() {
        for (let y = 0; y < this.rows; y++) {
            for (let x = 0; x < this.cols; x++) {
                if (this.board[y][x]) {
                    this.drawBlock(x, y, this.colors[this.board[y][x] - 1]);
                }
            }
        }
    }
    
    drawCurrentPiece() {
        for (let y = 0; y < this.currentPiece.shape.length; y++) {
            for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                if (this.currentPiece.shape[y][x]) {
                    this.drawBlock(
                        this.currentPiece.x + x,
                        this.currentPiece.y + y,
                        this.currentPiece.color
                    );
                }
            }
        }
    }
    
    drawBlock(x, y, color) {
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x * this.blockSize, y * this.blockSize, this.blockSize, this.blockSize);
        
        this.ctx.strokeStyle = '#222';
        this.ctx.strokeRect(x * this.blockSize, y * this.blockSize, this.blockSize, this.blockSize);
        
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        this.ctx.fillRect(x * this.blockSize, y * this.blockSize, this.blockSize, 4);
        
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        this.ctx.fillRect(x * this.blockSize, y * this.blockSize + this.blockSize - 4, this.blockSize, 4);
    }
    
    drawNextPiece() {
        this.nextCtx.fillStyle = '#111';
        this.nextCtx.fillRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);
        
        const blockSize = 20;
        const offsetX = (this.nextCanvas.width - this.nextPiece.shape[0].length * blockSize) / 2;
        const offsetY = (this.nextCanvas.height - this.nextPiece.shape.length * blockSize) / 2;
        
        for (let y = 0; y < this.nextPiece.shape.length; y++) {
            for (let x = 0; x < this.nextPiece.shape[y].length; x++) {
                if (this.nextPiece.shape[y][x]) {
                    this.nextCtx.fillStyle = this.nextPiece.color;
                    this.nextCtx.fillRect(
                        offsetX + x * blockSize,
                        offsetY + y * blockSize,
                        blockSize,
                        blockSize
                    );
                    
                    this.nextCtx.strokeStyle = '#222';
                    this.nextCtx.strokeRect(
                        offsetX + x * blockSize,
                        offsetY + y * blockSize,
                        blockSize,
                        blockSize
                    );
                }
            }
        }
    }
    
    updateDisplay() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('level').textContent = this.level;
        document.getElementById('lines').textContent = this.lines;
    }
    
    gameLoop() {
        if (!this.gameStarted || this.gameOver || this.paused) return;
        
        const now = Date.now();
        if (now - this.lastDrop > this.dropTime) {
            this.movePiece(0, 1);
            this.lastDrop = now;
        }
        
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}

const game = new Tetris();
