from game import *
from maps import Map
from path_finder import *

class MapNode():
    def __init__(self, x, y):
        self.parent: MapNode = None
        self.action = ""

        self.score = 0
        self.cost = 0

        self.x = x
        self.y = y
        self.h = 0
        self.code = 0
        self.spoil_code = 0
        self.player_egg = 0
        self.player_id = 0
        self.bomb = 0
        self.bomb_time = 0
        self.bomb_value = 0
    
class Map_V3(Map):
    def __init__(self):
        self.cols = 0
        self.rows = 0
        self.nodes = []

    def init_maps(self, game_state, pid):
        map_size = get_map_size(game_state)
        self.cols = map_size["cols"]
        self.rows = map_size["rows"]
        for x in range(self.cols):
            tmp = []
            for y in range(self.rows):
                node: MapNode = MapNode(x, y)
                code = game_state["map_info"]["map"][x][y]
                node.code = code
                tmp.append(node)
            self.nodes.append(tmp)
        
        # get egg cell
        eggs = game_state["map_info"]["dragonEggGSTArray"]
        for egg in eggs:
            x = egg["col"]
            y = egg["row"]
            node: MapNode = self.nodes[x][y]
            if egg["id"] == pid:
                node.player_egg = 1
            else:
                node.player_egg = 2

        # get player cell
        for player in game_state["map_info"]["players"]:
            x = player["currentPosition"]["col"]
            y = player["currentPosition"]["row"]
            node: MapNode = self.nodes[x][y]
            if player["id"] == pid:
                node.player_id = 1
            else:
                node.player_id = 2
        
    def update_map(self, game_state, pid):
        for x in range(self.cols):
            for y in range(self.rows):
                node: MapNode = self.nodes[x][y]
                code = game_state["map_info"]["map"][x][y]
                node.code = code
                node.bomb = 0
                node.h = 0
                self.score = 0
                self.cost = 0
                node.bomb_time -= TICK_DELAY
                node.spoil_code = 0
        # update spoils
        for spoil in game_state["map_info"]["spoils"]:
            x = spoil["col"]
            y = spoil["row"]
            node: MapNode = self.nodes[x][y]
            node.spoil_code = spoil["spoil_type"]
            if node.spoil_code == MYSTIC:
                self.score += MYSTIC_VALUE
            else:
                self.score += SPOIL_VALUE

    def get_free_neighbors(self, node: MapNode, is_in_bomb):
        neighbors = [
            ((node.x - 1, node.y), LEFT),
            ((node.x + 1, node.y), RIGHT),
            ((node.x, node.y - 1), UP),
            ((node.x, node.y + 1), DOWN)
        ]
        free_neighbors = []
        if node.code == GATE:
            return free_neighbors
        for neighbor in neighbors:
            location, direction = neighbor
            lx, ly = location
            if self.is_in_bounds(location) == False:
                continue
            neighbor_node: MapNode = self.nodes[lx][ly]
            if neighbor_node.code in BLOCK or neighbor_node.bomb == 1:
                continue
            if is_in_bomb == True and neighbor_node.bomb_time > 0 and neighbor_node.bomb_time <= (BOMB_DURATION + BOMB_DELTA_TIME):
                continue
            if is_in_bomb == False and neighbor_node.bomb_time > 0:
                continue
            free_neighbors.append({
                "node": neighbor_node,
                "action": direction
            })
        
        return sorted(
            free_neighbors,
            key= lambda x: x["node"].h,
            reverse=True
        )

            
    


    