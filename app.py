import sys
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, send, emit
import time
from threading import Thread
from base_agent import BaseAgent


import sockets.client as sk
from agent import Agent
import game

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

KEY = "9af19124-1e87-4ca6-b86e-056ca81009f8"
GAME_ID = "8506928b-b727-4b6d-a910-70a528b3fe17"
PLAYER1 = "player1-xxx"
PLAYER2 = "player2-xxx"
HOST = "http://localhost:3000"
GAME_FOUND = "Game Found"
GAME_NOT_FOUND = "Game Not Found"


@app.route("/", methods=["POST", "GET"])
def main():
    gameId = session.get("game", GAME_ID)
    pid = session.get("pid", PLAYER1)
    if request.method == "POST":
        gameId = request.form.get("game")
        pid = request.form.get("player")
        sk.connect_game(gameId, pid)
        session["pid"] = pid
        session["game"] = gameId

    move_thread = Thread(target=move, args=(sk.agent,))
    move_thread.start()
    return render_template("index.html", gameId=gameId, player=pid, players = sk.agent.game_state["map_info"]["players"])


@socketio.on("my event")
def handle_my_custom_event(json):
    print("received json: " + str(json))
    while True:
        emit("update data", {"data": sk.agent.game_state})
        time.sleep(1)


@socketio.on("move")
def on_move(code):
    print("Manual move", code)
    sk.move(code["data"])
    # game.show_map(maps, cols, rows)


@socketio.on("control ai")
def on_control_ai(data):
    game.control_ai = (data["data"])
    print(game.control_ai)


@socketio.on("next step")
def on_next_step(data):
    sk.agent.update_maps()
    x, y = sk.agent.current_position
    print(sk.agent.current_position)
    cols = sk.agent.maps.cols
    rows = sk.agent.maps.rows
    maps = sk.agent.maps
    maps.bfs(sk.agent.current_position, False)
    maps.show_around(sk.agent.current_position, 3)
    # print(maps.bomb_point_maps[x][y])
    # print(maps.spoil_maps[x][y])
    # print(maps.get_free_neighbors(sk.agent.current_position, False))
    # game.show_map(maps.heuristic_maps, cols, rows)
    # game.show_map(maps.bomb_point_maps, cols, rows)
    # game.show_map(maps.block_maps, cols, rows)
    # game.show_node_maps(maps.visited_maps, cols, rows)
    # for nb in nbs:
    #     for location, action in nb.items():
    #         lx, ly = location
    #         print("Neighbor:", location, maps.visited_maps[lx][ly].parent.location)
    sk.move(sk.agent.next_move())
    # sk.agent.next_move()
    pass
    

def move(agent: BaseAgent):
    print("Move")
    while True:
        if agent.is_start == 0:
            sk.move(game.STOP)
        elif game.control_ai == "start":
            if agent.complete_move == True or agent.stop_time > game.MAX_STOP_TIME:
                sk.move(agent.next_move())
                agent.complete_move = False
                agent.stop_time = 0
            else:
                agent.stop_time += game.TICK_DELAY
        time.sleep(game.TICK_DELAY/1000)

def main(port):
    if port:
        socketio.run(app, port=port, debug=True)
    else:
        socketio.run(app, debug=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(None)
