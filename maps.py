from game import *
from path_finder import *


class Map:
    def __init__(self):
        self.cols = 0
        self.rows = 0

        self.maps = []
        self.spoil_maps = []
        self.block_maps = []
        self.danger_maps = []
        self.bomb_point_maps = []
        self.visited_maps = []
        self.heuristic_maps = []

    def show_around(self, location, size):
        print("Print around", size)
        x, y = location
        for j in range(max(y - size, 0), min(y + size + 1, self.rows)):
            for i in range(max(x - size, 0), min(x + size + 1, self.cols)):
                value = self.danger_maps[i][j]
                print("%4d" % value, end="")
            print()

    def init_maps(self, game_state):
        map_size = get_map_size(game_state)
        self.cols = map_size["cols"]
        self.rows = map_size["rows"]
        # init maps
        self.maps = [[0] * self.rows for _ in range(self.cols)]
        self.spoil_maps = [[0] * self.rows for _ in range(self.cols)]
        self.block_maps = [[0] * self.rows for _ in range(self.cols)]
        self.danger_maps = [[0] * self.rows for _ in range(self.cols)]
        self.bomb_point_maps = [[0] * self.rows for _ in range(self.cols)]
        self.heuristic_maps = [[0] * self.rows for _ in range(self.cols)]
        for x in range(self.cols):
            tmp = []
            for y in range(self.rows):
                location = (x, y)
                tmp.append(Node(None, location, STOP))
            self.visited_maps.append(tmp)
        # update maps
        # self.update_map(game_state)
    
    def reset_maps(self):
        for x in range(self.cols):
            for y in range(self.rows):
                self.maps[x][y] = 0
                self.spoil_maps[x][y] = 0
                self.block_maps[x][y] = 0
                self.danger_maps[x][y] = max(0, self.danger_maps[x][y] - TICK_DELAY)
                self.bomb_point_maps[x][y] = 0
                self.heuristic_maps[x][y] = 0
                self.visited_maps[x][y] = Node(None, (x, y), STOP)

    def update_map(self, game_state):
        # process maps
        for pos_x in range(self.cols):
            for pos_y in range(self.rows):
                cell_code = game_state["map_info"]["map"][pos_y][pos_x]
                # calc maps
                self.maps[pos_x][pos_y] = cell_code
                # calc block
                if cell_code in BLOCK_VALUES:
                    self.block_maps[pos_x][pos_y] = BLOCK
                elif cell_code == GATE:
                    self.spoil_maps[pos_x][pos_y] = -12
    
    def is_in_bounds(self, location):
        posX, posY = location
        if posX < 0 or posX >= self.cols or posY < 0 or posY >= self.rows:
            return False
        return True
    
    def get_free_neighbors(self, location, is_in_bomb):
        x, y = location
        neighbors = [
            ((x - 1, y), LEFT),
            ((x + 1, y), RIGHT),
            ((x, y - 1), UP),
            ((x, y + 1), DOWN),
        ]
        free_neighbors = []
        if self.maps[x][y] == GATE:
            return free_neighbors

        for neighbor in neighbors:
            location, direction = neighbor
            lx, ly = location
            if self.is_in_bounds(location) == False or self.block_maps[lx][ly] == BLOCK:
                continue
            if self.danger_maps[lx][ly] == 0:
                free_neighbors.append({location: direction})
            elif is_in_bomb and self.danger_maps[lx][ly] > (BOMB_DURATION + BOMB_DELTA_TIME):
                free_neighbors.append({location: direction})

        return free_neighbors
    
    def bfs(self, start, is_in_bomb):
        visited_maps = self.visited_maps
        visit_queue = []
        start_x, start_y = start
        visited_maps[start_x][start_y].is_visited = VISITED
        visited_maps[start_x][start_y].val = self.spoil_maps[start_x][start_y]
        visit_queue.append(visited_maps[start_x][start_y])

        while len(visit_queue) > 0:
            cur_node: Node = visit_queue.pop(0)
            cost = cur_node.cost + 1
            val = cur_node.val
            neighbors = self.get_free_neighbors(cur_node.location, is_in_bomb)
            # print(cur_node.location)

            for neighbor in neighbors:
                for location, action in neighbor.items():
                    x, y = location
                    tmp_node: Node = visited_maps[x][y]
                    if tmp_node.is_visited == 0:
                        tmp_node.cost = cost
                        tmp_node.val = val + self.spoil_maps[x][y]
                        tmp_node.parent = cur_node
                        tmp_node.action = action
                        tmp_node.is_visited = VISITED
                        visit_queue.append(tmp_node)
                    # print("BFS: ", tmp_node.location, tmp_node.val)
                    
        return visited_maps
    



    
    
    

        