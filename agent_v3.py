import random
import traceback
from base_agent import BaseAgent
from game import *
from map_v3 import Map_V3, MapNode
from maps import Map
from path_finder import *
from game_data_sample import *


class AgentV3(BaseAgent):
    def __init__(self, pid, gameId):
        self.pid = pid
        self.gameId = gameId
        self.game_state = game_data

        self.is_start = 0
        self.delay_bomb = 0
        self.stop_time = 0
        self.complete_move = True
        # speed
        self.speed = 0
        self.enemy_speed = 0

        self.maps: Map_V3 = Map_V3()

    def update_maps(self):
        self.speed = self.cur_info["speed"]
        self.enemy_speed = self.oth_info["speed"]
        self.maps.update_map(self.game_state, self.pid)
        for bomb in self.game_state["map_info"]["bombs"]:
            self.update_bomb(bomb)
        self.maps.update_heuristic_maps(self.delay_bomb == 0)
        self.maps.update_bomb_score_maps()

    def next_move(self):
        tactic, action = self.find_tactic()
        print(tactic, action)
        if tactic != DROP_BOMB:
            self.delay_bomb = max(0, self.delay_bomb - TICK_DELAY)
        else :
            self.delay_bomb = self.cur_info["delay"]
        return action
    
    def find_tactic(self):
        x, y = self.current_position
        cur_node: MapNode = self.maps.nodes[x][y]
        if cur_node.code == PLACE:
            return (STAY, "")
        # if in bomb go out bomb
        if cur_node.bomb_time > 0:
            target = self.find_target_in_bomb()
            if target:
                action = get_action(target)
                return (OUT_BOMB, action[:MAX_STEP])
            else:
                target = self.find_slowest_bomb()
                action = get_action(target)
                return (OUT_BOMB, action[:MAX_STEP])
        # if dont have bomb, go farm
        target = self.go_farm_score()
        score_action = get_action(self.go_farm_score())
        score_cost = len(score_action)
        if self.delay_bomb > 0 and score_cost > 0:
            return (FARM_SCORE, score_action[:MAX_STEP])
        # check drop bomb in current position
        drop_bomb_target: MapNode = self.drop_bomb()
        drop_bomb_action = get_action(drop_bomb_target)
        drop_bomb_cost = len(drop_bomb_action)
        if drop_bomb_cost > 0 and drop_bomb_target.code != GATE:
            if cur_node.bomb_score > 0:
                if cur_node.bomb_score > 1:
                    return (DROP_BOMB, BOMB + drop_bomb_action[:MAX_STEP])
                elif drop_bomb_cost < score_cost:
                    return (DROP_BOMB, BOMB + drop_bomb_action[:MAX_STEP])
                elif score_cost == 0:
                    return (DROP_BOMB, BOMB + drop_bomb_action[:MAX_STEP])

        # if cant drop bomb, chose go farm score or go drop bomb
        go_bomb_target = self.go_drop_bomb()
        go_bomb_action = get_action(go_bomb_target)
        go_bomb_cost = len(go_bomb_action)
        if go_bomb_cost > 0:
            if go_bomb_cost < 2*score_cost and score_cost > 0 and score_cost < MAX_STEP:
                return (GO_BOMB, go_bomb_action[:MAX_STEP])
            elif score_cost == 0:
                return (GO_BOMB, go_bomb_action[:MAX_STEP])

        if score_cost > 0:
            return (FARM_SCORE, score_action[:MAX_STEP])
        
        return (STAY, "")
    
    def go_drop_bomb(self):
        self.maps.bfs(self.current_position, is_in_bomb=False)
        targets = []
        near_targets = []
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: MapNode = self.maps.nodes[x][y]
                if node.parent is None or node.bomb_time > 0 or node.bomb_score <= 0:
                    continue
                if node.cost <= NEAR_STEP:
                    near_targets.append(node)
                else:
                    targets.append(node)
        
        target: MapNode = None
        if near_targets:
            target = max(near_targets, key=lambda x: (x.path_score, -x.cost, x.h))
        elif targets:
            target = min(targets, key=lambda x: (x.cost, x.h))
        return target
    
    def go_farm_score(self):
        # find way go get score
        self.maps.bfs(self.current_position, is_in_bomb=False)
        targets = []
        near_targets = []
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: MapNode = self.maps.nodes[x][y]
                if node.parent is None or node.bomb_time > 0 or node.score <= 0:
                    continue
                if node.cost <= NEAR_STEP:
                    near_targets.append(node)
                else:
                    targets.append(node)
        
        target: MapNode = None
        if near_targets:
            target = max(near_targets, key=lambda x: (x.path_score, x.h, -x.cost))
        elif targets:
            target = min(targets, key=lambda x: (x.cost, x.h))
        return target

    
    def check_can_drop_bomb(self):
        action = ""
        x, y = self.current_position
        cur_node: MapNode = self.maps.nodes[x][y]
        if self.delay_bomb == 0 and cur_node.bomb_score > 0:
            action += self.drop_bomb()
        return action
    
    def drop_bomb(self):
        x, y = self.current_position
        bomb = {
            "col": x,
            "row": y, 
            "playerId": self.pid,
            "remainTime": BOMB_DEPLAY
        }
        self.update_clone_bomb_maps()
        self.update_bomb(bomb)
        # print("Add bomb at:", x, y, bomb["remainTime"])
        next_target = self.find_target_in_bomb()
        self.rollback_bomb_maps()
        # print("Actions bomb", actions)
        return next_target
    
    def update_clone_bomb_maps(self):
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: MapNode = self.maps.nodes[x][y]
                node.clone_bomb_time = node.bomb_time
                node.clone_bomb = node.bomb
    
    def rollback_bomb_maps(self):
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: MapNode = self.maps.nodes[x][y]
                node.bomb_time = node.clone_bomb_time
                node.bomb = node.clone_bomb
    
    def get_move(self):
        target = self.find_target()
        actions = []
        # print("Target", target.x, target.y)
        if target:
            actions = get_path_actions(get_path(target))
        return "".join(actions)
    
    def find_target(self):
        x, y = self.current_position
        node: MapNode = self.maps.nodes[x][y]
        if node.bomb_time > 0:
            target = self.find_target_in_bomb()
        else:
            target = self.find_target_out_bomb()
        return target
    
    def find_slowest_bomb(self):
        targets = []
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: MapNode = self.maps.nodes[x][y]
                if node.parent is None:
                    continue
                targets.append(node)
        if targets:
            return max(targets, key=lambda x: (x.bomb_time, -x.cost, x.h))

    
    def find_target_in_bomb(self):
        # print("find way go out bomb")
        self.maps.bfs(self.current_position, is_in_bomb=True)
        # self.maps.show()
        gate_nodes = []
        targets = []
        near_targets = []
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: MapNode = self.maps.nodes[x][y]
                if node.parent is None or node.bomb_time > 0:
                    continue
                if node.code == GATE:
                    gate_nodes.append(node)
                elif node.cost <= NEAR_STEP:
                    near_targets.append(node)
                else:
                    targets.append(node)
        
        if near_targets:
            return max(near_targets, key=lambda x: (x.path_score, x.h, -x.cost))
        if targets:
            return min(targets, key=lambda x: (x.cost, -x.h))
        if gate_nodes:
            return min(gate_nodes, key=lambda x: x.cost)
            
        
    def find_target_out_bomb(self):
        self.maps.bfs(self.current_position, is_in_bomb=False)
        # self.maps.show()
        max_step = calc_number_step(self.speed, TICK_DELAY)
        targets = []
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: MapNode = self.maps.nodes[x][y]
                if node.parent and node.bomb_time <= 0:
                    targets.append(node)

        targets = sorted(
            targets,
            key=lambda x: (x.score, x.bomb_score, x.h, -x.cost),
            reverse=True
        )
        for target in targets[:4]:
            print(target.x, target.y, target.score)
        if len(targets) == 0:
            return
        # get target in step
        # for target in targets:
        #     if target.cost <= max_step:
        #         print("aaaaaaaaaaaaaaaaaaaaa 1111111111")
        #         return target
        return targets[0]
        
    def update_bomb(self, bomb):
        bx = bomb["col"]
        by = bomb["row"]
        owner_info = self.get_info_by_id(bomb["playerId"])
        bomb_range = get_bomb_range(owner_info)
        
        bomb_node: MapNode = self.maps.nodes[bx][by]
        bomb_node.bomb = 1
        if bomb_node.bomb_time == 0:
            bomb_node.bomb_time = bomb["remainTime"] + BOMB_DURATION
        else:
            bomb_node.bomb_time = min(bomb_node.bomb_time, bomb["remainTime"] + BOMB_DURATION)
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
                if bomb_node.code in BOMB_BLOCK:
                    break
                if bomb_node.code == ROAD:
                    if bomb_node.bomb_time == 0:
                        bomb_node.bomb_time = bomb["remainTime"] + BOMB_DURATION
                    else:
                        bomb_node.bomb_time = min(bomb_node.bomb_time, bomb["remainTime"] + BOMB_DURATION)
                    
    


