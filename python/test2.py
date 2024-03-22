import sys
import random
from queue import Queue
from queue import PriorityQueue
import collections

n = 200
robot_num = 10
berth_num = 10
boat_num = 5
N = 210


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
    :param ch: 地图[][]='.'or'B'
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

# 机器人
class Robot:
    def __init__(self, startX=0, startY=0, goods=0, status=0, mbx=0, mby=0):
        # 当前位置坐标， 泊位位置
        self.x = startX
        self.y = startY
        self.goods = goods  # 0-未携带物品 1-携带物品
        self.status = status    # 0-恢复状态 1-正常运行状态
        self.mbx = mbx
        self.mby = mby
        self.next = None

        # 存储0，1，2，3的指示，例如[0, 2, 3, 1, 1]
        self.route = None

    def get_route(self, q: Queue):
        # 寻到路径后，将路径队列赋予当前机器人
        # 路径查找直接使用route出队
        self.route = q

    def next_pos(self):
        """
        通过x，y和route算出下一个位置的坐标
        :return: 下一个位置的坐标，例如（1，2），若队列为空，返回0
        """
        # 这里计算坐标
        if not self.route.empty():
            order = self.route.get()
            if order == 0:
                self.next = (self.x + 1, self.y)
            elif order == 1:
                self.next = (self.x - 1, self.y)
            elif order == 2:
                self.next = (self.x, self.y - 1)
            elif order == 3:
                self.next = (self.x, self.y + 1)
            else:
                raise ValueError("Item in route must be 0, 1, 2, 3")
            return self.next
        else:
            return None


class Goods:
    def __init__(self, x_pos, y_pos, price, birthday):
        self.x = x_pos
        self.y = y_pos
        self.price = price
        self.time_left = 1000  # 20s * 50fps
        self.cost_time = []  # 大小为berth_num的列表
        self.route = []  # 大小为berth_num的列表
        # 在这里调用寻路方法，找到当前物品到所有泊位的时间及路径
        # 填充cost_time和route
        self.birthday = birthday
        self.least_time = 10000
        # 在这里调用寻路方法，找到当前物品到所有泊位的时间及路径
        # 填充cost_time和route
        for b in berth:
            route_to_berth = a_star((self.x, self.y), (b.x, b.y), ch)
            self.route.append(route_to_berth)
            self.cost_time.append(len(route_to_berth))
            self.least_time = min(self.least_time, self.cost_time[-1])
            print(route_to_berth, self.route, self.cost_time, self.least_time)


robot = [Robot() for _ in range(robot_num + 10)]


# 泊位
class Berth:
    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self.x = x
        self.y = y
        self.transport_time = transport_time
        self.loading_speed = loading_speed
        self.performance_list = []  # 性价比列表，存储元组
        self.boat_id = -1    # 该泊位停靠船的id，没有船：-1
        self.load_num = 0   # 该泊位已装载货物个数

    def refresh_performance(self, new_good: Goods):
        """
        将新物品添加到性价比列表中
        :param good: 物品
        :return: None
        """
        # 存储的元组形式为（物品id，物品性价比）
        # 查找物品到当前泊位的时间
        # 计算性价比，插入排序
        berth_id = berth_dict[(self.x, self.y)]
        # if not berth_id:
        #     raise ValueError("Berth id can't be list")
        print(new_good.price, new_good.least_time, new_good.route[berth_id])
        value = new_good.price / (new_good.least_time + len(new_good.route[berth_id]))
        self.performance_list.append(((new_good.x, new_good.y), value))
        self.performance_list.sort(key=lambda x: x[1], reverse=True)

    def load_to_boat(self):
        if self.boat_id == -1:
            return 0
        if self.load_num > 0:
            left = boat[self.boat_id].left_space()
            load = min(self.loading_speed, self.load_num, left)
            self.load_num -= load
            boat[self.boat_id].load(load)
            return load


berth = [Berth() for _ in range(berth_num + 10)]


# 轮船
class Boat:
    def __init__(self, num=0, pos=0, status=0):
        self.num = num  # 船容积
        self.pos = pos  # 目标泊位id  虚拟点：-1
        self.status = status    # 0-运输中 1-装货状态/运输完成 2-泊位外等待
        self.load_num = 0   # 船已装载货物个数
        self.next_pos = 1 # 01010101

    def isFull(self):
        return self.num == self.load_num

    def left_space(self):
        return self.num - self.load_num

    def load(self, num=0):
        if self.left_space() < num:
            return
        if self.pos != -1 and self.status == 1:
            self.load_num += num

    def set_next_pos(self):
        self.next_pos = (self.next_pos + 1) % 2


boat = [Boat() for _ in range(boat_num)]

money = 0
boat_capacity = 0
id = 0
ch = []
gds = [[(0, 0) for _ in range(N)] for _ in range(N)]

# 存储物品的字典，用于快速索引相应物品
goods_dict = collections.defaultdict(list)

# 存储泊位的字典，用于快速索引相应泊位
berth_dict = collections.defaultdict(list)

# 机器人行动指令列表，这里只存走的命令（0，1，2，3），不涉及装货拿货，不动就置-1
robot_order_list = [-1 for _ in range(robot_num)]
# 船舶指令列表，装货，去虚拟点，从虚拟点回来     -2不动，-1go虚拟点
boat_order_list = [-2 for _ in range(boat_num)]

def Init():
    map_file = '../maps/map1.txt'
    berth_file = '../maps/map1_berth_config.txt'
    with open(map_file, 'r') as f:
        for line in f.readlines():
            ch.append([c for c in line])
    with open(berth_file, 'r') as f:
        for line in f.readlines():
            berth_list = [int(c) for c in line.split(sep=" ")]
            id = berth_list[0]
            berth[id].x = berth_list[1]
            berth[id].y = berth_list[2]
            berth[id].transport_time = berth_list[3]
            berth[id].loading_speed = berth_list[4]
            berth_dict[(berth[id].x, berth[id].y)] = id
    # boat_capacity = int(input())
    for i in range(boat_num):
        # boat[i].num = int(input())
        boat[i].num = (i+1)*100    # okk = input()
    print("OK")
    sys.stdout.flush()


def Input():
    id, money = map(int, input().split(" "))
    num = int(input())
    for i in range(num):
        x, y, val = map(int, input().split())
        # TODO new_gds
        new_good = Goods(x, y, val, id)
        # 字典中添加当前物品，键值是坐标
        for b in berth:
            b.refresh_performance(new_good)
        goods_dict[(x, y)] = new_good
        gds[x][y] = (val, 1000)
    for i in range(robot_num):
        robot[i].goods, robot[i].x, robot[i].y, robot[i].status = map(int, input().split())
    for i in range(5):
        boat[i].status, boat[i].pos = map(int, input().split())
    # okk = input()
    check_boat_pos()
    return id


def find_goods(robot: Robot, cur_frame):
    # 根据robot当前所在泊位，找到性价比最高的物品
    # 确保到物品的时间大于等于物品剩余时间
    # 由于有可能因为碰撞等待导致超时，这里需要再详细考虑
    # 选定物品，然后把这个物品从物品变量里删除掉
    # 直接把物品存的route代入robot里
    # 目标船的容量减1
    berth_id = berth_dict[(robot.x, robot.y)]
    berth_cur = berth[berth_id]
    for goodAndVal in berth_cur.performance_list:
        good = goods_dict[goodAndVal[0]]
        time_left = cur_frame - good.birthday
        if time_left > len(good.route[berth_id]):
            route_temp = good.route
            for i, val in enumerate(route_temp):
                if val == 0:
                    route_temp[i] = 1
                elif val == 1:
                    route_temp[i] = 0
                elif val == 2:
                    route_temp[i] = 3
                elif val == 3:
                    route_temp[i] = 2
                else:
                    raise ValueError("Route reserve failed, num in route must be 0, 1, 2, 3")
            robot.route = route_temp
            clear_goods(good)
            break
        elif time_left - 1000 <= 0:
            clear_goods(good)


def check_boat_pos():
    # 记录每帧输入的船的位置和状态，同步更新泊位
    # 每个船只负责两个泊位，来回切换
    for i in range(boat_num):
        if boat[i].status == 1:
            if boat[i].pos == -1:
                boat[i].load_num = 0
                boat[i].set_next_pos()
                boat[i].pos = boat[i].next_pos + i * 2
                # ship i boat[i].pos
                boat_order_list[i] = boat[i].pos
            else:
                berth[boat[i].pos].boat_id = i

        elif boat[i].status == 2:
            # TODO: 将船ship到新的泊位
            pass


def update_berth(mbx, mby):
    # 每次卸货后更新berth
    berth_id = -1
    for i in range(berth_num):
        if berth[i].x <= mbx <= (berth[i].x + 3) and berth[i].y <= mby <= (berth[i].y + 3):
            berth_id = i

    if berth_id == -1:
        return

    berth[berth_id].load_num += 1

    # for i in range(boat_num):
    #     if boat[i].pos == berth_id and boat[i].status == 1:
    #         boat[i].load_num += 1
    #         return


def berth_load_boat_go():
    # 所有berth装货到船上，船满了前往虚拟点
    for i in range(berth_num):
        berth[i].load_to_boat()

    for i in range(boat_num):
        if boat[i].isFull():
            # go i
            boat_order_list[i] = -1

            berth[boat[i].pos].boat_id = -1
            boat[i].pos = -1
            boat[i].status = 0


def clear_goods(good: Goods):
    """
    用于清除物品，包括物品被选中或消失
    :param good: 要清除的物品
    :return: none
    """
    goods_dict[(good.x, good.y)] = []
    for b in berth:
        for i, item in enumerate(b.performance_list):
            if item[0] == (good.x, good.y):
                b.performance_list.pop(i)
                break


def update_gds(gds):
    for i in range(len(gds)):
        for j in range(len(gds[i])):
            temp_list = list(gds[i][j])
            if gds[i][j][1] > 0:
                temp_list[1] -= 1
                # gds[i][j][1] -= 1
            if gds[i][j][1] == 0:
                temp_list[0] = 0
                # gds[i][j][0] = 0
            gds[i][j] = tuple(temp_list)
    return gds


def init_robot_route():
    for bot in robot:
        # 以下可以优化为如何为初始bot分配合适的berth，先用随机的方式做
        berth_id = random.randint(0, len(berth) - 1)
        bot.route = a_star((bot.x, bot.y), (berth[berth_id].x + 3, berth[berth_id].y + 3), ch)


if __name__ == "__main__":
    # 初始化物品，机器人，船舶，地图的状态
    Init()
    init_robot_route()
    for zhen in range(1, 15001):
        # 新的一帧到来时，需要更新物品，机器人，船舶的状态
        # 首先更新物品的状态
        # 新到的物品全部初始化，并存入一个变量方便查找
        gds = update_gds(gds)
        # 指令重置
        robot_order_list = [-1 for _ in range(robot_num)]
        boat_order_list = [-2 for _ in range(boat_num)]

        id = Input()

        # 首先确定所有空闲机器人
        # 通过循环确定没有路径的机器人
        # 循环中为每个机器人确定要去的位置
        for bot in robot:
            if bot.goods == 0 and bot.route == []:
                find_goods(bot, zhen)
            # if判断，如果该机器人空闲，通过find_goods方法找到要去的位置，确定路径
        # 机器人当前位置列表，以及下一格位置列表，按机器人id顺序存储
        cur_pos = []
        next_pos = []
        # # 机器人行动指令列表，这里只存走的命令（0，1，2，3），不涉及装货拿货，不动就置-1
        # robot_order_list = []
        # # 船舶指令列表，装货，去虚拟点，从虚拟点回来
        # boat_order_list = []
        # for循环遍历机器人，填充上述列表
        for bot in robot:
            # 填充列表，这里保证所有机器人都有下一个位置
            cur_pos.append((bot.x, bot.y))
            next_pos.append(bot.next_pos())

        # TODO 按照机器人当前任务的潜在价值排序，暂时按从0到9写死
        robot_sorted_by_val = [i for i in range(robot_num)]
        # 碰撞处理
        for index in robot_sorted_by_val:
            bot = robot_sorted_by_val[index]
            # 下一步被优先级高的先占了或下一步的位置有优先级更高的机器人，重新寻路
            if next_pos[index] in next_pos[:index - 1] or next_pos[index] in cur_pos[:index - 1]:
                bot.route = a_star((bot.x, bot.y), (bot.mbx, bot.mby), ch)
                next_pos[index] = bot.next_pos()

        # 机器人碰撞处理
        # 第一步，互相走到对方位置
        # 即如果next_pos能在cur_pos查到（且下标不同），并且被查到的cur_pos的下标索引的next_pos是一开始判断点的cur_pos
        # 想一种处理方法
        # 第二步，走向相同位置
        # next_pos内部判断，若有重复的，选择一个行动，其余的robot_order_list置0，next_pos变为cur_pos
        # 这里注意，停下来可能导致本来不会碰撞到的发生碰撞

        for i in range(robot_num):
            cur_x = cur_pos[i][0]
            cur_y = cur_pos[i][1]
            next_x = next_pos[i][0]
            next_y = next_pos[i][1]
            if cur_x==next_x and cur_y==next_y:
                robot_order_list[i] = -1
            elif cur_x==next_x and cur_y+1==next_y:
                robot_order_list[i] = 0
            elif cur_x==next_x and cur_y-1==next_y:
                robot_order_list[i] = 1
            elif cur_x-1==next_x and cur_y==next_y:
                robot_order_list[i] = 2
            elif cur_x+1==next_x and cur_y==next_y:
                robot_order_list[i] = 3
            else:
                raise ValueError("Not a valid robot")

        # 确定机器人指令，如果机器人的next_pos和其目标x（mbx）目标y（mby）吻合，则其应当在move后执行装货卸货命令，并将状态置为空闲或重置route
        # move，根据robot_order_list确定机器人指令
        step = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        for i in range(robot_num):
            order = robot_order_list[i]
            if order == -1:     # 跳过该机器人
                continue

            # move i order
            print("move", i, order)

            robot[i].x += step[order][0]
            robot[i].y += step[order][1]

            if robot[i].x == robot[i].mbx and robot[i].y == robot[i].mby:
                if robot[i].goods == 1:
                    # pull i
                    print("pull", i)

                    robot[i].goods = 0
                    update_berth(robot[i].mbx, robot[i].mby)

                if robot[i].goods == 0:
                    # get i
                    print("get", i)

                    robot[i].goods = 1
                    # 机器人取货指令（获取货物实例）
                    cur_goods = goods_dict[(robot[i].x, robot[i].y)]
                    robot[i].route = cur_goods.route

        berth_load_boat_go()

        for i in range(boat_num):
            order = boat_order_list[i]
            if order == -2:     # 跳过该船
                continue
            elif order == -1:     # goto 虚拟点
                # go i
                print("go", i)
            else:
                #ship i boat[i].pos
                print("ship", i, boat[i].pos)


        # 卸货，机器人的status是有货并且到达目标点，则pull，此时机器人在泊位，状态为空闲
        # 卸货后更新船舶容量状态
        # 检查船舶状态，船舶已满的立刻出发去虚拟点,即设定boat_order_list为去虚拟点
        # 装货，机器人的status是无货并且到达目标点，则put，将物品的route更新到机器人上，更新机器人状态
        # 所有在港船舶执行装货命令，设定boat_order_list

        # 所有到达虚拟点的船舶选择返回的泊位，按照如下优先级进行选择
        # 1.选择空闲泊位
        # 2.选择潜在物品价值最高泊位
        # 3.选择到达时间最早的泊位
        # 设定boat_order_list

        # 根据robot_order_list，boat_order_list进行输出

        # for i in range(robot_num):
        #     # print("move", i, random.randint(0, 3))
        #     strategy = get_strategy(robot[i], ch, berth, gds)
        #     sys.stdout.flush()
        print("OK")
        sys.stdout.flush()
