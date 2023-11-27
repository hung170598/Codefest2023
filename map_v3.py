from datetime import datetime
import time
from game import *
from maps import Map
from path_finder import *

class MapNode():
    def __init__(self, x, y):
        # path to target
        self.parent: MapNode = None
        self.action = ""
        # score and cost for path finding
        self.score = 0
        self.path_score = 0
        self.cost = 0
        # location
        self.x = x
        self.y = y
        # heuristic
        self.h = 0
        # object
        self.code = 0
        self.spoil_code = 0
        self.player_egg = 0
        self.player_id = 0
        self.bomb = 0
        # bomb remain time
        self.bomb_time = 0
        # clone bome
        self.clone_bomb = 0
        self.clone_bomb_time = 0
        # score if drop bomb
        self.bomb_score = 0
    
class Map_V3(Map):
    def __init__(self):
        # map size
        self.cols = 0
        self.rows = 0
        # map node
        self.nodes = []
        # player infor
        self.my_player = {}
        self.enemy_player = {}
        # number object in map
        self.balk_number = 0
        self.mystic_number = 0
        self.spoil_number = 0

    def init_maps(self, game_state, pid):
        map_size = get_map_size(game_state)
        self.cols = map_size["cols"]
        self.rows = map_size["rows"]
        for x in range(self.cols):
            tmp = []
            for y in range(self.rows):
                node: MapNode = MapNode(x, y)
                code = game_state["map_info"]["map"][y][x]
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
    
    def update_player_info(self, game_state, pid):
        for player in game_state["map_info"]["players"]:
            if player["id"] == pid:
                self.my_player = player
            else:
                self.enemy_player = player
        
    def update_map(self, game_state, pid):
        self.balk_number = 0
        self.mystic_number = 0
        self.spoil_number = 0
        self.update_player_info(game_state, pid)

        for x in range(self.cols):
            for y in range(self.rows):
                node: MapNode = self.nodes[x][y]
                code = game_state["map_info"]["map"][y][x]
                node.code = code
                node.bomb = 0
                node.h = 0
                node.score = 0
                node.cost = 0
                node.parent = None
                node.action = ""
                node.bomb_time = max(node.bomb_time - TICK_DELAY, 0)
                node.bomb_score = 0
                node.spoil_code = 0
                if node.code == BALK:
                    self.balk_number += 1
                elif node.code == GATE:
                    node.score = -2
        # update spoils
        for spoil in game_state["map_info"]["spoils"]:
            x = spoil["col"]
            y = spoil["row"]
            node: MapNode = self.nodes[x][y]
            # print
            node.spoil_code = spoil["spoil_type"]
            if node.spoil_code == MYSTIC:
                self.mystic_number += 1
                node.score += MYSTIC_VALUE
            else:
                self.spoil_number += 1
                node.score += SPOIL_VALUE

    def update_bomb_score_maps(self):
        for x in range(self.cols):
            for y in range(self.rows):
                node: MapNode = self.nodes[x][y]
                self.update_bomb_score_cell(node)

    def update_bomb_score_cell(self, node: MapNode):
        if node.code != ROAD or node.player_id > 1 or node.bomb > 0:
            return
        bomb_range = get_bomb_range(self.my_player)
        # check left
        for x in range(node.x - 1, max(0, node.x - bomb_range) - 1, -1):
            tmp_node: MapNode = self.nodes[x][node.y]
            node.bomb_score += self.calc_bomb_score_with_node(tmp_node)
            if tmp_node.code in BOMB_BLOCK or tmp_node.player_id == 2:
                break
        # check right
        for x in range(node.x + 1, min(self.cols, node.x + bomb_range) + 1):
            tmp_node: MapNode = self.nodes[x][node.y]
            node.bomb_score += self.calc_bomb_score_with_node(tmp_node)
            if tmp_node.code in BOMB_BLOCK or tmp_node.player_id == 2:
                break
        # check up
        for y in range(node.y - 1, max(0, node.y - bomb_range) - 1, -1):
            tmp_node: MapNode = self.nodes[node.x][y]
            node.bomb_score += self.calc_bomb_score_with_node(tmp_node)
            if tmp_node.code in BOMB_BLOCK or tmp_node.player_id == 2:
                break
        # check down
        for y in range(node.y + 1, min(self.rows, node.y + bomb_range) + 1):
            tmp_node: MapNode = self.nodes[node.x][y]
            node.bomb_score += self.calc_bomb_score_with_node(tmp_node)
            if tmp_node.code in BOMB_BLOCK or tmp_node.player_id == 2:
                break

    def calc_bomb_score_with_node(self, tmp_node: MapNode):
        bomb_score = 0
        if tmp_node.code == BALK:
            bomb_score = 1
        elif tmp_node.player_egg == 2:
            bomb_score = min(self.enemy_player[PLAYER_SCORE], 2)
        elif tmp_node.player_egg == 1:
            bomb_score = -(self.my_player[PLAYER_SCORE], 2)
        elif tmp_node.player_id == 2:
            bomb_score = 2
        return bomb_score

    def update_heuristic_maps(self, have_bomb: bool):
        for x in range(self.cols):
            for y in range(self.rows):
                node: MapNode = self.nodes[x][y]
                self.update_heuristic_cell(node, have_bomb)

    def update_heuristic_cell(self, node: MapNode, have_bomb):
        if node.code == WALL or node.code == PLACE:
            return
        if node.code == GATE:
            node.h = HEURISTIC.GATE.value
            return
        if node.code == EGG:
            if node.player_egg == 1:
                self.update_heuristic_my_egg(node)
            else:
                self.update_heuristic_enemy_egg(node)
            return
        # if node.code == BALK and have_bomb:
        #     self.update_heuristic_balk(node)
        #     return
        if node.spoil_code > 0:
            self.update_heuristic_spoil(node)

    def update_heuristic_spoil(self, node: MapNode):
        node.h += node.score
        for x in range(self.cols):
            for y in range(self.rows):
                if x != node.x or y != node.y:
                    tmp_node: MapNode = self.nodes[x][y]
                    if tmp_node.code == ROAD:
                        distance = manhattan_distance(x, y, node.x, node.y)
                        tmp_node.h += 1.0 * node.score / distance

    def update_heuristic_balk(self, node: MapNode):
        for x in range(self.cols):
            for y in range(self.rows):
                if x != node.x or y != node.y:
                    tmp_node: MapNode = self.nodes[x][y]
                    if tmp_node.code == ROAD:
                        distance = manhattan_distance(x, y, node.x, node.y)
                        tmp_node.h += 1.0 * HEURISTIC.BALK.value / distance

    def update_heuristic_my_egg(self, node: MapNode):
        if self.enemy_player[PLAYER_SCORE] == 0:
            return
        node.h = max(HEURISTIC.MY_EGG.value, -self.enemy_player[PLAYER_SCORE])
        for x in range(self.cols):
            for y in range(self.rows):
                if x != node.x or y != node.y:
                    tmp_node: MapNode = self.nodes[x][y]
                    if tmp_node.code == ROAD:
                        distance = manhattan_distance(x, y, node.x, node.y)
                        tmp_node.h += 1.0 * node.h / distance

    def update_heuristic_enemy_egg(self, node: MapNode):
        if self.enemy_player[PLAYER_SCORE] == 0:
            return
        node.h = min(HEURISTIC.ENEMY_EGG.value, self.enemy_player[PLAYER_SCORE])
        for x in range(self.cols):
            for y in range(self.rows):
                if x != node.x or y != node.y:
                    tmp_node: MapNode = self.nodes[x][y]
                    if tmp_node.code == ROAD:
                        distance = manhattan_distance(x, y, node.x, node.y)
                        tmp_node.h += 1.0 * node.h / distance

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
            if neighbor_node.code in BLOCK_VALUES or neighbor_node.bomb == 1 or neighbor_node.player_id > 0 or neighbor_node.player_egg > 0:
                continue
            if is_in_bomb == True and neighbor_node.bomb_time > 0:
                bomb_time = neighbor_node.bomb_time - (node.cost + 2)*TICK_DELAY 
                if bomb_time <= (BOMB_DURATION + BOMB_DELTA_TIME):
                    continue
            if is_in_bomb == False and neighbor_node.bomb_time > 0:
                continue
            if is_in_bomb == False and neighbor_node.score < 0:
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
    
    def reset_maps_for_bfs(self):
        for x in range(self.cols):
            for y in range(self.rows):
                node: MapNode = self.nodes[x][y]
                node.cost = 0
                node.parent = None
                node.action = ""
                node.path_score = 0
    
    def bfs(self, start, is_in_bomb):
        visit_queue = []
        visited_map = [[0] * self.rows for _ in range(self.cols)]
        start_x, start_y = start
        start_node: MapNode = self.nodes[start_x][start_y]
        visited_map[start_x][start_y] = VISITED
        visit_queue.append(start_node)
        # print("Start bfs at ", start_x, start_y, "time", time.time_ns())

        while len(visit_queue) > 0:
            cur_node: MapNode = visit_queue.pop(0)
            # print("Visited ", cur_node.x, cur_node.y)
            cost = cur_node.cost + 1
            neighbors = self.get_free_neighbors(cur_node, is_in_bomb)
            # print(cur_node.location)

            for neighbor in neighbors:
                node: MapNode = neighbor["node"]
                action = neighbor["action"]
                if visited_map[node.x][node.y] == 0:
                    node.parent = cur_node
                    node.path_score += cur_node.path_score
                    node.cost = cost
                    node.action = action
                    visited_map[node.x][node.y] = VISITED
                    visit_queue.append(node)
        # print("End bfs at ", start_x, start_y, "time", time.time_ns())
    
    def show(self):
        print("My info", self.my_player)
        print("Enemy info", self.enemy_player)
        print("Balk number", self.balk_number)
        print("Mystic number", self.mystic_number)
        print("Spoil number", self.spoil_number)
        print("Max step", calc_number_step(self.my_player["speed"], TICK_DELAY))
        for y in range(self.rows):
            for x in range(self.cols):
                node: MapNode = self.nodes[x][y]
                # print("%6.2f" % node.h, end=" ")
                print("%4d" % node.bomb_score, end=" ")
                # print(node.parent, end=" ")
            print()

            
    