import random
import traceback
from game import *
from maps import Map
from path_finder import *
from game_data_sample import *


class BaseAgent:
    def __init__(self, pid, gameId):
        self.pid = pid
        self.gameId = gameId
        self.game_state = game_data

        self.is_start = 0
        self.delay_bomb = 0

        self.maps: Map = Map()

    def next_move(self):
        """
        This method is called each time your Agent is required to choose an action
        """
        actions = ""
        x, y = self.current_position
        try:
            self.update_maps()
            if self.delay_bomb == 0 and self.maps.bomb_point_maps[x][y] > 0:
                actions += self.drop_bomb()
                if actions == "":
                    actions += self.get_move()
            else:
                self.delay_bomb = max(0, self.delay_bomb - TICK_DELAY)
                actions += self.get_move()
            print("Actions", actions)
        except Exception as e:
            traceback.print_exc()
        return actions

    def drop_bomb(self):
        actions = "b"
        my_info = self.cur_info
        self.delay_bomb = BOMB_DEPLAY - EGG_DEPLAY * min(
            MAX_DELAY_EGG, my_info["dragonEggDelay"]
        )
        return actions

    def find_target(self):
        # need update in this function
        pass

    def get_move(self):
        target = self.find_target()
        actions = ""
        # print("Target", target.location)
        if target:
            actions = get_path_actions(get_path(target))
        return "".join(actions)

    @property
    def current_position(self):
        for player in self.game_state["map_info"]["players"]:
            if player["id"] == self.pid:
                return (
                    player["currentPosition"]["col"],
                    player["currentPosition"]["row"],
                )
        return (0, 0)

    @property
    def cur_info(self):
        for player in self.game_state["map_info"]["players"]:
            if player["id"] == self.pid:
                return player

    @property
    def oth_info(self):
        for player in self.game_state["map_info"]["players"]:
            if player["id"] != self.pid:
                return player

    def get_info_by_id(self, id):
        for player in self.game_state["map_info"]["players"]:
            if player["id"] == id:
                return player

    def start_game(self):
        self.maps.init_maps(self.game_state)
        self.is_start = 1
        print("Game Start")

    def update_maps(self):
        self.maps.reset_maps()
        self.maps.update_map(self.game_state)
        self.process_value_maps()
        self.process_block_maps()
        self.process_bombs_maps()
        self.process_bomb_point_maps()

    def process_bomb_point_maps(self):
        for x in range(self.maps.cols):
            for y in range(self.maps.rows):
                self.maps.bomb_point_maps[x][y] = self.calc_cell_bomb_val(
                    x, y, self.cur_info
                )

    def calc_cell_bomb_val(self, bx, by, cur_info):
        if self.maps.maps[bx][by] != ROAD:
            return 0
        bomb_point = 0
        bomb_range = get_bomb_range(cur_info)
        # check left
        for i in range(bomb_range):
            x = bx - i - 1
            y = by
            location = (x, y)
            if self.maps.is_in_bounds(location) == False:
                break
            cell_code = self.maps.maps[x][y]
            bomb_point += self._get_bomb_point(location, cell_code)
            if self.maps.block_maps[x][y] == BLOCK and self.maps.maps[x][y] != GATE:
                break
        # check right
        for i in range(bomb_range):
            x = bx + i + 1
            y = by
            location = (x, y)
            if self.maps.is_in_bounds(location) == False:
                break
            cell_code = self.maps.maps[x][y]
            bomb_point += self._get_bomb_point(location, cell_code)
            if self.maps.block_maps[x][y] == BLOCK and self.maps.maps[x][y] != GATE:
                break
        # check up
        for i in range(bomb_range):
            x = bx
            y = by - (i + 1)
            location = (x, y)
            if self.maps.is_in_bounds(location) == False:
                break
            cell_code = self.maps.maps[x][y]
            bomb_point += self._get_bomb_point(location, cell_code)
            if self.maps.block_maps[x][y] == BLOCK and self.maps.maps[x][y] != GATE:
                break
        # check down
        for i in range(bomb_range):
            x = bx
            y = by + (i + 1)
            location = (x, y)
            if self.maps.is_in_bounds(location) == False:
                break
            cell_code = self.maps.maps[x][y]
            bomb_point += self._get_bomb_point(location, cell_code)
            if self.maps.block_maps[x][y] == BLOCK and self.maps.maps[x][y] != GATE:
                break
        # return
        return bomb_point

    def _get_bomb_point(self, location, cell_code):
        bomb_point = 0
        if cell_code == BALK:
            bomb_point += 1
        if self._is_egg_cell(location) == 2:
            bomb_point += 1
        elif self._is_egg_cell(location) == 1:
            bomb_point = -20
        elif self._is_oth_player_cell(location):
            bomb_point += PLAYER_BOMB_POINT
        return bomb_point

    def _is_egg_cell(self, location):
        eggs = self.game_state["map_info"]["dragonEggGSTArray"]
        x, y = location
        for egg in eggs:
            if x == egg["col"] and y == egg["row"]:
                if egg["id"] == self.pid:
                    return 1
                return 2
        return 0

    def _is_oth_player_cell(self, location):
        oth_player = self.oth_info
        x, y = location
        if x == oth_player["currentPosition"]["col"] and y == oth_player["currentPosition"]["row"]:
            return True
        return False

    def process_value_maps(self):
        my_info = self.cur_info
        maps = self.maps

        for spoil in self.game_state["map_info"]["spoils"]:
            if spoil["spoil_type"] == SPEED:
                maps.spoil_maps[spoil["col"]][spoil["row"]] = 2
            elif spoil["spoil_type"] == ATT:
                maps.spoil_maps[spoil["col"]][spoil["row"]] = 2
            elif spoil["spoil_type"] == DELAY:
                maps.spoil_maps[spoil["col"]][spoil["row"]] = 2
            elif spoil["spoil_type"] == MYSTIC:
                maps.spoil_maps[spoil["col"]][spoil["row"]] = MYSTIC_VALUE

    def process_block_maps(self):
        my_info = self.cur_info
        oth_info = self.oth_info
        block_maps = self.maps.block_maps

        block_maps[oth_info["currentPosition"]["col"]][
            oth_info["currentPosition"]["row"]
        ] = BLOCK
        # block_maps[my_info["currentPosition"]["col"]][my_info["currentPosition"]["row"]] = BLOCK

    def process_bombs_maps(self):
        for bomb in self.game_state["map_info"]["bombs"]:
            self.process_bomb(bomb)

    def process_bomb(self, bomb):
        bx = bomb["col"]
        by = bomb["row"]

        # bomb_time = bomb["remainTime"] + BOMB_DURATION*1000
        block_maps = self.maps.block_maps
        danger_maps = self.maps.danger_maps
        owner_info = self.get_info_by_id(bomb["playerId"])
        bomb_range = get_bomb_range(owner_info)
        # min(MAX_ATT_RANGE, owner_info["dragonEggAttack"] + 1)
        bomb_time = bomb["remainTime"] + BOMB_DURATION

        block_maps[bx][by] = BLOCK
        danger_maps[bx][by] = bomb_time
        # check left
        self._add_bomb_time(bx, by, bomb_range, bomb_time, -1, 0)
        # check right
        self._add_bomb_time(bx, by, bomb_range, bomb_time, 1, 0)
        # check up
        self._add_bomb_time(bx, by, bomb_range, bomb_time, 0, -1)
        # check down
        self._add_bomb_time(bx, by, bomb_range, bomb_time, 0, 1)

    def _add_bomb_time(self, bx, by, bomb_range, bomb_time, dx, dy):
        for i in range(1, bomb_range + 1):
            x = bx + dx * i
            y = by + dy * i
            location = (x, y)
            if self.maps.is_in_bounds(location) and self.maps.block_maps[x][y] != BLOCK:
                self.maps.danger_maps[x][y] = max(
                    self.maps.danger_maps[x][y], bomb_time
                )
            elif self.maps.maps[x][y] != GATE:
                break

