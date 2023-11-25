control_ai = "start"
# control
LEFT = "1"
RIGHT = "2"
UP = "3"
DOWN = "4"
BOMB = "b"
STOP = "x"
# map
ROAD = 0
WALL = 1
BALK = 2
GATE = 3
PLACE = 4
EGG = 5
BLOCK_VALUES = [WALL, BALK, EGG, PLACE, GATE]
# spoil
ATT = 4
DELAY = 5
SPEED = 3
MYSTIC = 6
# cell value
BLOCK = 1
BOMB_BLOCK = -1000
MYSTIC_VALUE = 1
# Time ms
BOMB_DEPLAY = 2000
EGG_DEPLAY = 400
TICK_DELAY = 500
BOMB_DURATION = 1000
# time bomb begin action
BOMB_DELTA_TIME = 500
# max 
MAX_DELAY_EGG = 4
MAX_SPEED_EGG = 5
MAX_ATT_EGG = 5
MAX_ATT_RANGE = 4
# visit map
VISITED = 1
PLAYER_BOMB_POINT = 2


def get_cell_code(maps, location):
    posX, posY = location
    return maps[posX][posY]


def get_bomb_range(player):
    return min(MAX_ATT_RANGE, player["dragonEggAttack"] + 1)


def get_map_size(game_state):
    return game_state["map_info"]["size"]


def is_in_bounds(game_state, location):
    posX, posY = location
    map_size = get_map_size(game_state)
    if posX < 0 or posX >= map_size["cols"] or posY < 0 or posY >= map_size["rows"]:
        return False
    return True


def get_bombs(game_state):
    return game_state["map_info"]["bombs"]


def get_info_by_id(game_state, id):
    for player in game_state["map_info"]["players"]:
        if player["id"] == id:
            return player


def is_occupied(occupied_maps, location):
    x, y = location
    # print(location, occupied_maps[x][y])
    return occupied_maps[x][y] != BLOCK


def is_bomb_block(occupied_maps, location):
    x, y = location
    # print(location, occupied_maps[x][y])
    return occupied_maps[x][y] == BOMB_BLOCK


# given our current location, return only surrounding tiles that are free
def get_free_neighbors(game_data, val_maps, occ_maps, location):
    x, y = location
    neighbors = [
        ((x - 1, y), LEFT, val_maps[x - 1][y]),
        ((x + 1, y), RIGHT, val_maps[x + 1][y]),
        ((x, y - 1), UP, val_maps[x][y - 1]),
        ((x, y + 1), DOWN, val_maps[x][y + 1]),
    ]
    neighbors.sort(key=lambda neighbor: neighbor[2], reverse=True)
    free_neighbors = []
    cur_val = val_maps[x][y]
    count_not_bomb = 0

    for neighbor in neighbors:
        tile, direction, val = neighbor
        if is_in_bounds(game_data, tile) == False:
            continue
        tile_x, tile_y = tile
        # print("check_neighbor_in_bomb", is_occupied(occ_maps, tile))
        if is_occupied(occ_maps, tile) == False:
            continue
        if val >= 0:
            free_neighbors.append({tile: direction})
            count_not_bomb += 1
        if cur_val < 0 and count_not_bomb == 0:
            free_neighbors.append({tile: direction})

    return free_neighbors


def check_neighbor_in_bomb(val_cur, val_neightbor):
    if val_cur >= MYSTIC_VALUE:
        return val_neightbor >= MYSTIC_VALUE
    return True

def show_map(maps, cols, rows):
    for pos_y in range(rows):
        for pos_x in range(cols):   
            print("%4d" % maps[pos_x][pos_y], end="")
        print()


def show_node_maps(maps, cols, rows):
    for pos_y in range(rows):
        for pos_x in range(cols):   
            print("%4d" % maps[pos_x][pos_y].cost, end="")
        print()


