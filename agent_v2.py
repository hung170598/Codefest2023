from base_agent import BaseAgent
from path_finder import *
from game import *


class AgentV2(BaseAgent):
    def __init__(self, pid, gameId):
        super().__init__(pid, gameId)

    def find_target(self):
        super().find_target()
        x, y = self.current_position
        danger_maps = self.maps.danger_maps
        if danger_maps[x][y] > 0:
            target = self.find_target_if_in_bomb()
        else:
            target = self.find_target_if_not_in_bomb()
        return target
    
    # def calc_reverse_path(self, node):

    def drop_bomb(self):
        actions = "b"
        x, y = self.current_position
        bomb = {
            "col": x,
            "row": y, 
            "playerId": self.pid,
            "remainTime": 3000
        }
        self.process_bomb(bomb)
        next_target = self.find_target_if_in_bomb()
        if next_target:
            actions += "".join(get_path_actions(get_path(next_target)))
            self.delay_bomb = BOMB_DEPLAY - EGG_DEPLAY * min(
                MAX_DELAY_EGG, self.cur_info["dragonEggDelay"]
            )
        else: 
            actions = ""
        return actions

    def find_target_if_in_bomb(self):
        self.maps.bfs(self.current_position, True)
        list_target = []
        visited_maps = self.maps.visited_maps
        danger_maps = self.maps.danger_maps

        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: Node = visited_maps[x][y]
                if node.parent is None:
                    continue
                if danger_maps[x][y] > 0:
                    continue
                list_target.append(node)
        list_target = sorted(
            list_target, 
            key= lambda x: x.cost
        )
        if list_target:
            return list_target[0]
        return None
    
    def find_target_if_not_in_bomb(self):
        self.maps.bfs(self.current_position, False)
        list_target = []
        visited_maps = self.maps.visited_maps
        danger_maps = self.maps.danger_maps
        bomb_point_maps = self.maps.bomb_point_maps

        cx, cy = self.current_position
        cur_node = visited_maps[cx][cy]
        cur_node.val = bomb_point_maps[cx][cy]
        list_target.append(cur_node)

        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                node: Node = visited_maps[x][y]
                if node.parent is None:
                    continue
                if danger_maps[x][y] > 0:
                    continue
                node.val = node.val + bomb_point_maps[x][y]
                list_target.append(node)
        list_target = sorted(
            list_target, 
            key= lambda x: (x.val, -x.cost),
            reverse=True
        )
        if list_target:
            return list_target[0]
        return None

