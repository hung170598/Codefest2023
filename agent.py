import random
import traceback
from game import *
from path_finder import *
from game_data_sample import *


class Agent:
    def __init__(self, pid, gameId):
        self.game_state = game_data
        self.is_start = 0
        self.delay_bomb = 0
        self.occupied_maps = []
        self.maps = []
        self.val_maps = []
        self.boom_val_maps = []
        self.pid = pid
        self.gameId = gameId
        self.visited_maps = []

    def start_game(self):
        map_size = get_map_size(self.game_state)
        cols = map_size["cols"]
        rows = map_size["rows"]
        self.occupied_maps = [[0] * rows for _ in range(cols)]
        self.maps = [[0] * rows for _ in range(cols)]
        self.val_maps = [[0] * rows for _ in range(cols)]
        self.boom_val_maps = [[0] * rows for _ in range(cols)]
        print("Game Start")
        self.is_start = 1

    def next_move(self):
        """
        This method is called each time your Agent is required to choose an action
        """

        ###### CODE HERE ######
        actions = ""
        try:
            # print("Moveeeeeeeeeeeeee")
            # self.delay_bomb = max(0, self.delay_bomb - TICK_DELAY)
            # actions += self.move()

            if self.delay_bomb == 0:
                actions += self.drop_bomb()
            else:
                self.delay_bomb = max(0, self.delay_bomb - TICK_DELAY)
                actions += self.move()
            print("Actions", actions)
        except Exception as e:
            traceback.print_exc()
        return actions

    def get_current_position(self):
        for player in self.game_state["map_info"]["players"]:
            if player["id"] == self.pid:
                return (
                    player["currentPosition"]["col"],
                    player["currentPosition"]["row"],
                )
        return (0, 0)

    def process_maps(self):
        map_size = get_map_size(self.game_state)
        cols = map_size["cols"]
        rows = map_size["rows"]
        self.occupied_maps = [[0] * rows for _ in range(cols)]
        self.boom_val_maps = [[0] * rows for _ in range(cols)]

        # check other play position
        oth_info = self.get_oth_info()
        self.occupied_maps[oth_info["currentPosition"]["col"]][
            oth_info["currentPosition"]["row"]
        ] = BLOCK

        for pos_x in range(cols):
            for pos_y in range(rows):
                # process maps
                cell_code = self.game_state["map_info"]["map"][pos_y][pos_x]
                self.maps[pos_x][pos_y] = cell_code
                if self.val_maps[pos_x][pos_y] < MYSTIC_VALUE:
                    self.val_maps[pos_x][pos_y] = min(0, self.val_maps[pos_x][pos_y] + TICK_DELAY*1000)
                else:
                    self.val_maps[pos_x][pos_y] = 0
                if cell_code > 0:
                    self.occupied_maps[pos_x][pos_y] = BLOCK
                self.boom_val_maps[pos_x][pos_y] = self.calc_cell_boom_val(pos_x, pos_y)

        self._process_value_maps()
        for bomb in self.game_state["map_info"]["bombs"]:
            self._process_bomb(bomb)

    def _get_bomb_val(self, location, cell_code):
        bomb_val = 0
        if cell_code == BALK:
            bomb_val += 1
        if self._is_egg_cell(location) == 2:
            bomb_val += 1
        if self._is_egg_cell(location) == 1:
            bomb_val = -20
        return bomb_val

    def calc_cell_boom_val(self, bx, by):
        bomb_val = 0
        my_info = self.get_cur_info()
        if self.occupied_maps[bx][by] == BLOCK:
            return bomb_val
        bomb_range = min(3, my_info["dragonEggAttack"] + 1)
        # check left
        for i in range(bomb_range):
            x = bx - i - 1
            y = by
            location = (x, y)
            if is_in_bounds(self.game_state, location) == False:
                break
            cell_code = get_cell_code(self.maps, location)
            bomb_val += self._get_bomb_val(location, cell_code)
            if cell_code != ROAD:
                break
        # check right
        for i in range(bomb_range):
            x = bx + i + 1
            y = by
            location = (x, y)
            if is_in_bounds(self.game_state, location) == False:
                break
            cell_code = get_cell_code(self.maps, location)
            bomb_val += self._get_bomb_val(location, cell_code)
            if cell_code != ROAD:
                break
        # check up
        for i in range(bomb_range):
            x = bx
            y = by - i - 1
            location = (x, y)
            if is_in_bounds(self.game_state, location) == False:
                break
            cell_code = get_cell_code(self.maps, location)
            bomb_val += self._get_bomb_val(location, cell_code)
            if cell_code != ROAD:
                break
        # check down
        for i in range(bomb_range):
            x = bx
            y = by + i + 1
            location = (x, y)
            if is_in_bounds(self.game_state, location) == False:
                break
            cell_code = get_cell_code(self.maps, location)
            bomb_val += self._get_bomb_val(location, cell_code)
            if cell_code != ROAD:
                break
        return bomb_val

    def _process_value_maps(self):
        my_info = self.get_cur_info()
        for spoil in self.game_state["map_info"]["spoils"]:
            if self.val_maps[spoil["col"]][spoil["row"]] < MYSTIC_VALUE:
                continue
            if spoil["spoil_type"] != MYSTIC:
                self.val_maps[spoil["col"]][spoil["row"]] = 1
            if spoil["spoil_type"] == SPEED:
                self.val_maps[spoil["col"]][spoil["row"]] = 1
            if spoil["spoil_type"] == ATT and my_info["dragonEggAttack"] < 2:
                self.val_maps[spoil["col"]][spoil["row"]] = 1
            if spoil["spoil_type"] == DELAY and my_info["dragonEggDelay"] < 3:
                self.val_maps[spoil["col"]][spoil["row"]] = 1

    def _add_bomb_time(self, bx, by, bomb_range, bomb_time, dx, dy):
        for i in range(1, bomb_range + 1):
            x = bx + dx * i
            y = by + dy * i
            location = (x, y)
            if (
                is_in_bounds(self.game_state, location)
                and get_cell_code(self.maps, location) == ROAD
            ):
                self.val_maps[x][y] = -bomb_time
            else:
                break

    def _process_bomb(self, bomb):
        bx = bomb["col"]
        by = bomb["row"]
        bomb_time = bomb["remainTime"] + BOMB_DURATION*1000
        owner_info = get_info_by_id(self.game_state, bomb["playerId"])
        bomb_range = min(3, owner_info["dragonEggAttack"] + 1)

        self.occupied_maps[bx][by] = BLOCK
        self.val_maps[bx][by] = -bomb_time
        self.boom_val_maps[bx][by] = 0

        # check left
        self._add_bomb_time(bx, by, bomb_range, bomb_time, -1, 0)

        # check right
        self._add_bomb_time(bx, by, bomb_range, bomb_time, 1, 0)

        # check up
        self._add_bomb_time(bx, by, bomb_range, bomb_time, 0, -1)

        # check down
        self._add_bomb_time(bx, by, bomb_range, bomb_time, 0, 1)

    def get_cur_info(self):
        for player in self.game_state["map_info"]["players"]:
            if player["id"] == self.pid:
                return player

    def get_oth_info(self):
        for player in self.game_state["map_info"]["players"]:
            if player["id"] != self.pid:
                return player

    def _is_egg_cell(self, location):
        eggs = self.game_state["map_info"]["dragonEggGSTArray"]
        x, y = location
        for egg in eggs:
            if x == egg["col"] and y == egg["row"]:
                if egg["id"] == self.pid:
                    return 1
                return 2
        return 0

    # def find_out_bomb(self):
    #     print("Find out bomb: ")
    #     start_x, start_y = self.get_current_position()
    #     self.visited_maps = bfs(self.game_state, self.occupied_maps, self.val_maps, self.get_current_position())
    #     bomb = {"row": start_y, "col": start_x, "remainTime": self.delay_bomb, "playerId": self.pid}
    #     self._process_bomb(bomb)

    #     map_size = get_map_size(self.game_state)
    #     cols = map_size["cols"]
    #     rows = map_size["rows"]
    #     min_cost = 10000000
    #     max_value = 0
    #     target: Node = self.visited_maps[start_x][start_y]

    #     for x in range(cols):
    #         for y in range(rows):
    #             node: Node = self.visited_maps[x][y]
    #             cell_val = node.val
    #             cell_val += self.boom_val_maps[x][y]
    #             if node.parent is not None :
    #                 if cell_val/node.cost > max_value:
    #                     max_value = cell_val/node.cost
    #                     target = node
    #                     min_cost = target.cost
    #                 elif node.cost < min_cost and cell_val/node.cost == max_value:
    #                     target = node
    #                     min_cost = target.cost

    #     return target

    def _is_target(self, x, y, cur_target: Node):
        node: Node = self.visited_maps[x][y]
        cell_val = self.val_maps[x][y]
        cell_val += self.boom_val_maps[x][y]
        node_val = node.val
        cur_x, cur_y = cur_target.location
        # print("Node:", node.location, node.cost, node.val)

        if node.parent is None:
            return cur_target

        if self.val_maps[cur_x][cur_y] < 0 and cell_val >= 0:
            return node
        if cur_target.val < 0:
            if node.val > cur_target.val:
                return node
        if (
            cur_target.cost > 0
            and cur_target.val / cur_target.cost < node.val / node.cost
        ):
            return node
        return cur_target

    def find_target(self):
        self.visited_maps = bfs(
            self.game_state,
            self.occupied_maps,
            self.val_maps,
            self.get_current_position(),
        )

        map_size = get_map_size(self.game_state)
        cols = map_size["cols"]
        rows = map_size["rows"]
        min_cost = 10000000
        max_value = 0
        start_x, start_y = self.get_current_position()
        target: Node = self.visited_maps[start_x][start_y]

        for x in range(cols):
            for y in range(rows):
                target = self._is_target(x, y, target)
                # node: Node = self.visited_maps[x][y]
                # cell_val = node.val
                # cell_val += self.boom_val_maps[x][y]
                # if node.parent is not None:
                #     if cell_val / node.cost > max_value:
                #         max_value = cell_val / node.cost
                #         target = node
                #         min_cost = target.cost
                #     elif node.cost < min_cost and cell_val / node.cost == max_value:
                #         target = node
                #         min_cost = target.cost

        return target

    def drop_bomb(self):
        actions = "b"
        my_info = self.get_cur_info()
        self.delay_bomb = BOMB_DEPLAY - EGG_DEPLAY * min(
            MAX_EGG_DELAY, my_info["dragonEggDelay"]
        )
        return actions

    def move(self):
        target = self.find_target()
        # print("Target", target.location)
        return self.move_to_target(target)

    def move_to_target(self, target: Node):
        my_info = self.get_cur_info()
        if target.location is not None:
            actions = get_path_actions(get_path(self.occupied_maps, target))
        # print("Actions: ", actions)
        # if self.delay_bomb == 0:
        #     actions.append(BOMB)
        #     self.delay_bomb = BOMB_DEPLAY - EGG_DEPLAY*min(MAX_EGG_DELAY, my_info["dragonEggDelay"])
        return "".join(actions)

    def is_in_bombs(self):
        x, y = self.get_current_position()
        for bomb in get_bombs(self.game_state):
            if x == bomb["col"] and y == bomb["row"]:
                return True
        return False
