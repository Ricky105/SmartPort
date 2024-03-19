def Init(map_size, berth_num):
    ch = []
    for i in range(0, map_size):
        # 读入地图
        line = input()
        ch.append([c for c in line.split(sep=" ")])
    for i in range(berth_num):
        # 读入泊口信息
        line = input()
        berth_list = [int(c) for c in line.split(sep=" ")]
        id = berth_list[0]
        berth[id].x = berth_list[1]
        berth[id].y = berth_list[2]
        berth[id].transport_time = berth_list[3]
        berth[id].loading_speed = berth_list[4]
        berth_dict[(berth[id].x, berth[id].y)] = id