class Node:
    def __init__(self, parent=None, location=None, action=None):
        self.parent: Node = parent
        self.location = location
        self.action = action
        self.is_visited = 0
        self.val = 0
        self.cost = 0
        self.h = 0
        self.g = 0
        self.f = 0
        self.is_save = 0
        

def get_path(node: Node):
    path = []
    while node.parent is not None:
        # print(node.action, end= " ")
        path.append(node)
        node = node.parent
    return reversed(path)


def get_path_actions(path):
    actions = []
    for node in path:
        actions.append(node.action)
    return actions


def get_action(target):
    if target:
        action = get_path_actions(get_path(target))
        return ''.join(action)
    return ""

def manhattan_distance(x1, y1, x2, y2):
    distance = abs(x1 - x2) + abs(y1 - y2)
    return distance


# def bfs(game_state, occ_maps, val_maps, start):
#     visited_maps = []
#     visit_queue = []
#     map_size = get_map_size(game_state)
#     cols = map_size["cols"]
#     rows = map_size["rows"]
#     for x in range(cols):
#         tmp = []
#         for y in range(rows):
#             location = (x, y)
#             tmp.append(Node(None, location, STOP))
#         visited_maps.append(tmp)
#     start_x, start_y = start
#     visited_maps[start_x][start_y].is_visited = 2
#     visited_maps[start_x][start_y].val = val_maps[x][y]
#     visit_queue.append(visited_maps[start_x][start_y])
#     loop = 4

#     while visit_queue and loop > 0:
#         cur_node: Node = visit_queue.pop(0)
#         # print(cur_node.location)
#         # print("Cur node: ", cur_node.location, cur_node.val, cur_node.cost, cur_node.is_visited)
#         cur_x, cur_y = cur_node.location
#         cost = cur_node.cost + 1
#         val = cur_node.val
#         neighbors = get_free_neighbors(game_state, val_maps, occ_maps, cur_node.location)
#         # print(neighbors)

#         for neighbor in neighbors:
#             for location, action in neighbor.items():
#                 x, y = location
#                 tmp_node: Node = visited_maps[x][y]
#                 val += val_maps[x][y]
#                 # print("Neighbor node: ", tmp_node.location, tmp_node.cost, tmp_node.is_visited)
#                 if tmp_node.is_visited == 0:
#                     tmp_node.cost = cost
#                     tmp_node.val = val
#                     tmp_node.parent = cur_node
#                     tmp_node.action = action
#                     visit_queue.append(tmp_node)
#                 # elif tmp_node.is_visited > 0 and tmp_node.val < 0 and val > tmp_node.val:
#                 #     tmp_node.cost = cost
#                 #     tmp_node.val = val
#                 #     tmp_node.parent = cur_node
#                 #     tmp_node.action = action
#                 #     visit_queue.append(tmp_node)
#                 tmp_node.is_visited += 1

#     return visited_maps


# def astar(game_data, occ_maps, val_maps, start, target):

#     open_list = [Node(None, start, None)]
#     closed_list = []

#     max_loops = 200
#     counter = 0

#     while len(open_list) > 0 and counter <= max_loops:
#         # find the node with the lowest rank
#         curr_node = open_list[0]
#         curr_index = 0
#         for index, node in enumerate(open_list):
#             if node.f < curr_node.f:
#                 curr_node = node
#                 curr_index = index
#         # check if this node is the goal
#         if curr_node.location == target:
#             # print(f"~~~~~~~FOUND TARGET~~~~~~~")
#             return curr_node

#         # current = remove lowest rank item from OPEN
#         # add current to CLOSED
#         del open_list[curr_index]
#         closed_list.append(curr_node)

#         neighbors = get_free_neighbors(game_data, occ_maps, curr_node.location)
#         neighbor_nodes = []
#         for neighbor in neighbors:
#             for location, action in neighbor.items():
#                 neighbor_nodes.append(Node(None, location, action))

#         for neighbor in neighbor_nodes:
#             in_closed = False
#             in_open = False
#             # cost = g(current) + movementcost(current, neighbor)
#             node_x, node_y = curr_node.location
#             cost = curr_node.g + 1 - val_maps[node_x][node_y]
#             # if neighbor in OPEN and cost less than g(neighbor):
#             #   remove neighbor from OPEN, because new path is better
#             for index, node in enumerate(open_list):
#                 if neighbor.location == node.location and cost < neighbor.g:
#                     del open_list[index]
#                     in_open = True

#             # if neighbor in CLOSED and cost less than g(neighbor): ⁽²⁾
#             #   remove neighbor from CLOSED
#             for index, node in enumerate(closed_list):
#                 if neighbor.location == node.location and cost < neighbor.g:
#                     del closed_list[index]
#                     in_closed = True
#             # if neighbor not in OPEN and neighbor not in CLOSED:
#             #   set g(neighbor) to cost
#             #   add neighbor to OPEN
#             #   set priority queue rank to g(neighbor) + h(neighbor)
#             #   set neighbor's parent to current
#             if not in_open and not in_closed:
#                 neighbor.g = cost
#                 open_list.append(neighbor)
#                 neighbor.h = manhattan_distance(neighbor.location, target)
#                 neighbor.f = neighbor.g + neighbor.h
#                 neighbor.parent = curr_node

#         counter += 1
#     return Node(None, None, None)


# returns the manhattan distance between two tiles, calculated as:
# 	|x1 - x2| + |y1 - y2|

