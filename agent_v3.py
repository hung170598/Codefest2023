import random
import traceback
from base_agent import BaseAgent
from game import *
from map_v3 import Map_V3, MapNode
from maps import Map
from path_finder import *
from game_data_sample import *


class Agent_V3(BaseAgent):
    def __init__(self, pid, gameId):
        self.pid = pid
        self.gameId = gameId
        self.game_state = game_data

        self.is_start = 0
        self.delay_bomb = 0
        self.stop_time = 0
        self.complete_move = True

        self.maps: Map_V3 = Map_V3()

    def update_maps(self):
        self.maps.update_map(self.game_state, self.pid)
        for bomb in self.game_state["map_info"]["bombs"]:
            self.update_bomb(bomb)
        
    def update_bomb(self, bomb):
        bx = bomb["col"]
        by = bomb["row"]
        owner_info = self.get_info_by_id(bomb["playerId"])
        bomb_range = get_bomb_range(owner_info)

        bomb_node: MapNode = self.maps.nodes[bx][by]
        bomb_node.bomb = 1
        bomb_node.bomb_time = max(bomb_node.bomb_time, bomb["remainTime"] + BOMB_DURATION)
        self.update_bomb_time(bx, by, bomb_range, bomb, -1, 0)
        self.update_bomb_time(bx, by, bomb_range, bomb, 1, 0)
        self.update_bomb_time(bx, by, bomb_range, bomb, 0, -1)
        self.update_bomb_time(bx, by, bomb_range, bomb, 0, 1)

    def update_bomb_time(self, bx, by, bomb_range, bomb, dx, dy):
        for i in range(1, bomb_range + 1):
            x = bx + dx * i
            y = by + dy * i
            if self.maps.is_in_bounds((x, y)):
                bomb_node: MapNode = self.maps.nodes[x][y]
                if bomb_node.code not in BOMB_BLOCK:
                    break
                bomb_node.bomb_time = max(bomb_node.bomb_time, bomb["remainTime"] + BOMB_DURATION)
    
    def update_heuristic_maps(self):
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                self.update_heuristic_cell(x, y)

    def update_heuristic_cell(self, x, y):
        pass


        
