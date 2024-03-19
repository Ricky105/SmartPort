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
