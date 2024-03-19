from algorithm import a_star


class Boat:
    def __init__(self, capacity=0, pos=0, status=0):
        self.capacity = capacity
        # 所在泊位ID
        self.pos = pos
        # 状态 0-运输中,1正常运行,2泊外等待
        self.status = status
        # 当前储量
        self.load_num = 0
        # 下一步
        self.next_pos = -1

    def is_full(self):
        return self.capacity == self.load_num

    def left_space(self):
        return self.capacity - self.load_num

    def load(self, size):
        if self.left_space() < size:
            return
        if self.pos != -1 and self.status == 1:
            self.load_num += size

    def set_next_pos(self):
        self.next_pos = (self.next_pos + 1) % 2


class Goods:
    def __init__(self, x_pos, y_pos, price, birthday):
        self.x = x_pos
        self.y = y_pos
        self.price = price
        self.time_left = 1000  # 20s * 50fps
        self.cost_time = []  # 大小为berth_num的列表
        self.route = []  # 大小为berth_num的列表
        self.birthday = birthday
        self.least_time = 10000
    def add_route(self, berth_list, ch):
        # 在这里调用寻路方法，找到当前物品到所有泊位的时间及路径
        # 填充cost_time和route
        for b in berth_list:
            route_to_berth = a_star((self.x, self.y), (b.x, b.y), ch)
            self.route.append(route_to_berth)
            self.cost_time.append(len(route_to_berth))
            self.least_time = min(self.least_time, self.cost_time[-1])


class Berth:
    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self.x = x
        self.y = y
        self.transport_time = transport_time
        self.loading_speed = loading_speed
        # 存储泊口对于每个物品的性价比[((x, y), value), ...]
        self.performance_list = []
        # 当前泊口对应的船
        self.cur_boat = None

    def set_boat(self, boat: Boat):
        self.cur_boat = boat

    def refresh_performance(self, new_good: Goods):
        """
        将新物品添加到性价比列表中
        :param good: 物品
        :return: None
        """
        # 存储的元组形式为（物品id，物品性价比）
        # 查找物品到当前泊位的时间
        # 计算性价比，插入排序
        # TODO
        berth_id = berth_dict[(self.x, self.y)]
        if not berth_id:
            raise ValueError("Berth id can't be list")
        value = new_good.price / (new_good.least_time + len(new_good.route[berth_id]))
        self.performance_list.append(((new_good.x, new_good.y), value))
        self.performance_list.sort(key=lambda x: x[1], reverse=True)

    def load_to_boat(self):
        if self.boat_id == -1:
            return 0
        if self.load_num > 0:
            # TODO
            left = boat[self.boat_id].left_space()
            load = min(self.loading_speed, self.load_num, left)
            self.load_num -= load
            boat[self.boat_id].load(load)
            return load