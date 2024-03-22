from queue import PriorityQueue


def neighbors(current_pos, ch):
    m, n = len(ch), len(ch[0])
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors_pos = []
    for i in range(4):
        x, y = current_pos[0], current_pos[1]
        new_x, new_y = x + dirs[i][0], y + dirs[i][1]
        if 0 <= new_x < m and 0 <= new_y < n and ch[new_x][new_y] in ['.', 'B']:
            neighbors_pos.append((new_x, new_y))
    return neighbors_pos


def manhattan(current_pos, next_pos):
    return abs(current_pos[0] - next_pos[0]) + abs(current_pos[1] - next_pos[1])


def a_star(src_pos, target_pos, ch, max_step=15):
    """
    A*寻路算法
    :param src_pos: 源位置(x1, y1)
    :param target_pos: 目标位置(x2, y2)
    :param ch: 地图[][]='.'
    :param max_step: 最多步长设置 TODO
    :return: [x, x, ...] 0右移，1左移，2上移，3下移
    """
    frontier = PriorityQueue()
    frontier.put(src_pos, 0)
    came_from = {}
    cost_so_far = {}
    came_from[src_pos] = None
    cost_so_far[src_pos] = 0

    while not frontier.empty():
        current_pos = frontier.get()

        if current_pos == target_pos:
            break

        for next_pos in neighbors(current_pos, ch):
            new_cost = cost_so_far[current_pos] + 1
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + manhattan(current_pos, next_pos)
                frontier.put(next_pos, priority)
                came_from[next_pos] = current_pos

    if target_pos not in came_from:
        # 不可达
        return []

    # 从路径提取策略
    strategy = []
    current_pos = target_pos
    while current_pos != src_pos:
        pre_pos = came_from[current_pos]
        if pre_pos[0] - current_pos[0] == 0 and pre_pos[1] - current_pos[1] == -1:
            # right
            strategy.append(0)
        elif pre_pos[0] - current_pos[0] == 0 and pre_pos[1] - current_pos[1] == 1:
            # left
            strategy.append(1)
        elif pre_pos[0] - current_pos[0] == 1 and pre_pos[1] - current_pos[1] == 0:
            # up
            strategy.append(2)
        elif pre_pos[0] - current_pos[0] == -1 and pre_pos[1] - current_pos[1] == 0:
            # down
            strategy.append(3)
        current_pos = pre_pos

    return strategy[::-1]