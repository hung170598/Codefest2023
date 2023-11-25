const BLOCK_SIZE = 30;
const EMPTY_ID = 0;

const canvas = document.getElementById('board');
const ctx = canvas.getContext('2d');

const socket = io();

var COLS = 30;
var ROWS = 30;
var gameData = {};

ctx.canvas.width = COLS * BLOCK_SIZE;
ctx.canvas.height = ROWS * BLOCK_SIZE;

document.addEventListener('keydown', (e) => {
    code = '';
    switch (e.code) {
        case 'KeyW':
            code = '3';
            break;
        case 'KeyA':
            code = '1';
            break;
        case 'KeyS':
            code = '4';
            break;
        case 'KeyD':
            code = '2';
            break;
        case 'Space':
            code = 'b';
            break;
        case 'KeyQ':
            code = 'x';
            break;
        case 'KeyO':
            socket.emit('control ai', { data: "start" });
            break;
        case 'KeyP':
            socket.emit('control ai', { data: "stop" });
            break;
        case 'KeyN':
            socket.emit('next step', {});
            break;
    }
    if (code != '')
        socket.emit('move', { data: code });
})


class Board {
    constructor(ctx) {
        this.ctx = ctx;
        this.grid = this.generateEmptyMap();
    }

    generateEmptyMap() {
        return Array.from({ length: ROWS }, () => Array(COLS).fill(EMPTY_ID));
    }

    drawCell(posX, posY, value) {
        this.ctx.fillRect(posX * BLOCK_SIZE, posY * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
    }
}

board = new Board(ctx)
x = 1
y = 1

socket.on("update data", (data) => {
    gameData = data;
});

socket.on('connect', function () {
    socket.emit('my event', { data: 'I\'m connected!' });
});