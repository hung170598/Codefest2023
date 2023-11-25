import socketio
from base_agent import BaseAgent
from agent_v2 import AgentV2
from game import *
# from agent import Agent

sio = socketio.Client()
HOST = "http://127.0.0.1:3000"
sio.connect(HOST, wait_timeout=10)
agent: BaseAgent = AgentV2("", "")

def get_socket_client():
    return sio


def connect_game(gameId, pid):
    agent.gameId = gameId
    agent.pid = pid
    data = {"game_id": agent.gameId, "player_id": agent.pid}
    sio.emit("join game", data)


def move(code):
    if len(code) > 0:
    # print("Current possition: ", agentClient.get_current_position(), "code: ", get_cell_code(agentClient.maps, agentClient.get_current_position()))
    # print("Neighbors: ", get_free_neighbors(agentClient.game_state, agentClient.occupied_maps, agentClient.get_current_position()))
        sio.emit("drive player", {"direction": f"{code}"})


@sio.event
def connect():
    print("I'm connected!")


@sio.on("drive player")
def on_drive(data):
    # print("Current possition: ", agentClient.get_current_position(), "code: ", get_cell_code(agentClient.maps, agentClient.get_current_position()))
    # print("Neighbors: ", get_free_neighbors(agentClient.game_state, agentClient.occupied_maps, agentClient.get_current_position()))
    # print("drive player: ", data)
    pass


@sio.on("join game")
def on_join_game(data):
    print("Join game!")


@sio.on("ticktack player")
def on_ticktack(data):
    agent.game_state = data
    if agent.is_start == 0:
        agent.start_game()
    else:
        if data["tag"] == 'player:stop-moving' and data["player_id"] == agent.pid:
            # print("Complete move!")
            agent.complete_move = True
    # agent.update_maps()
