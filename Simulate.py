import random
import matplotlib.pyplot as plt
import csv
from math import dist

class Vehicle:
    def __init__(self,id) -> None:
        self.id = id
        self.x, self.y = 0, 0
        self.vx, self.vy = 0, 0
        self.ax, self.ay = 0, 0
        self.lane = 0 # 0 for top lane, 1 for bottom lane

    def update(self, dt):
        # 用当前速度和加速度更新位置
        self.x += self.vx * dt + 0.5 * self.ax * dt ** 2
        self.y += self.vy * dt + 0.5 * self.ay * dt ** 2
        # 用当前加速度更新速度
        self.vx += self.ax * dt
        self.vy += self.ay * dt

class Road:
    def __init__(self, length, width) -> None:
        self.length = length
        self.width = width
        self.vehicles = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def update(self, dt):
        dele = []
        for vehicle in self.vehicles:
            if vehicle.lane == 1:#下半车道
                # 基于其他车辆的位置计算自身车辆的加速度
                front_dis = [(v.x - vehicle.x) for v in self.vehicles if v.lane == vehicle.lane and v.id != vehicle.id \
                         and (v.x - vehicle.x) > 0 and (v.x - vehicle.x ) < 100\
                            and (v.y - vehicle.y) > -5 and (v.y - vehicle.y) < 5] # 距前方100m内的车的距离
                if len(front_dis) != 0:
                    vehicle.ax = -5 / min(front_dis)
                else: # 前方100m内没车，几乎匀速
                    vehicle.ax = random.uniform(-0.05,0.05)
                left_dis = [(v.y - vehicle.y) for v in self.vehicles if v.lane == vehicle.lane and v.id != vehicle.id\
                        and (v.y - vehicle.y) > 0 and (v.y - vehicle.y) < 25\
                            and (v.x - vehicle.x) > -5 and (v.x - vehicle.x) < 5] # 距左方25m内的车的距离
                right_dis = [(vehicle.y - v.y) for v in self.vehicles if v.lane == vehicle.lane and v.id != vehicle.id\
                             and (vehicle.y - v.y) > 0 and (vehicle.y - v.y) < 25\
                                and (v.x - vehicle.x) > -5 and (v.x - vehicle.x) < 5] # 距右方25m内的车的距离
                if len(left_dis) == 0 and len(right_dis) != 0:#左方没车,右方有车,向左加速
                    vehicle.ay = random.uniform(0,0.2) 
                elif len(left_dis) != 0 and len(right_dis) == 0:#左方有车，右方没车，向右加速
                    vehicle.ay = random.uniform(-0.2,0)
                elif len(left_dis) == 0 and len(right_dis) == 0:#左右都没车，几乎匀速
                    vehicle.ay = random.uniform(-0.05,0.05)
                else:#左右都有车
                    if min(left_dis) < min(right_dis):#左边的车离得较近
                        vehicle.ay = random.uniform(-0.2,0)
                    else:
                        vehicle.ay = random.uniform(0,0.2)

                # 更新车辆位置和速度
                vehicle.update(dt)
                # 控制不超出车道
                if vehicle.x > self.length or vehicle.x < 0:#离开系统
                    dele.append(vehicle.id)

                if vehicle.y > self.width / 2:
                    vehicle.y = self.width / 2 - random.uniform(1,10)
                elif vehicle.y < 0:
                    vehicle.y = random.uniform(1,10)
                # 控制不倒车
                if vehicle.vx < 0:
                    vehicle.vx = random.uniform(0,2.5)

            else:#上半车道
                front_dis = [(vehicle.x - v.x) for v in self.vehicles if v.lane == vehicle.lane and v.id != vehicle.id\
                             and (vehicle.x - v.x) > 0 and (vehicle.x - v.x) < 100\
                                and (vehicle.y - v.y) > -5 and (vehicle.y - v.y) < 5] #距前方100m内的车的距离
                if len(front_dis) != 0:
                    vehicle.ax = 5 / min(front_dis)
                else:#前方100m内没车，几乎匀速
                    vehicle.ax = random.uniform(-0.05,0.05)
                left_dis = [(vehicle.y - v.y) for v in self.vehicles if v.lane == vehicle.lane and v.id != vehicle.id\
                            and (vehicle.y - v.y) > 0 and (vehicle.y - v.y) < 25\
                                and (vehicle.x - v.x) > -5 and (vehicle.x - v.x) < 5] #距左方25m内的车的距离
                right_dis = [(v.y - vehicle.y) for v in self.vehicles if v.lane == vehicle.lane and v.id != vehicle.id\
                             and (v.y - vehicle.y) > 0 and (v.y - vehicle.y) < 25\
                                and (v.x - vehicle.x) > -5 and (v.x - vehicle.x) < 5]# 距右方25m内的车的距离
                if len(left_dis) == 0 and len(right_dis) != 0:#左方没车，右方有车
                    vehicle.ay = random.uniform(-0.2,0)
                elif len(left_dis) != 0 and len(right_dis) == 0:#左方有车，右方没车
                    vehicle.ay = random.uniform(0,0.2)
                elif len(left_dis) == 0 and len(right_dis) == 0:#左右都没车，几乎匀速
                    vehicle.ay = random.uniform(-0.05,0.05)
                else:#左右都有车
                    if min(left_dis) < min(right_dis):#左边的车离得较近
                        vehicle.ay = random.uniform(0,0.2)
                    else:
                        vehicle.ay = random.uniform(-0.2,0)
                #更新车辆位置和速度
                vehicle.update(dt)
                # 控制不超出车道
                if vehicle.x > self.length or vehicle.x < 0:#离开系统
                    dele.append(vehicle.id)
                if vehicle.y > self.width:
                    vehicle.y = self.width - random.uniform(1,10)
                elif vehicle.y < self.width / 2:
                    vehicle.y = self.width / 2 + random.uniform(1,10)
                #控制不倒车
                if vehicle.vx > 0:
                    vehicle.vx = random.uniform(-2.5,0)

    
                    
        remain = []
        for vehicle in self.vehicles:
            if vehicle.id in dele:
                continue
            remain.append(vehicle)
        self.vehicles = remain
            
ID = 0
SIMULTION_TIME = 100 #sec
TIME_STEP = 1 #sec
LONGTH = 4000 #m
WIDTH = 400 #m
R = 180


road = Road(LONGTH,WIDTH)

while ID < 15:
    vehicle = Vehicle(ID)
    vehicle.lane = random.randint(0,1)
    if vehicle.lane == 1:#下半车道
        vehicle.x = random.uniform(0, 500)
        vehicle.y = random.uniform(0, road.width / 2)
        vehicle.vx = random.uniform(30, 40)
        vehicle.vy =  random.uniform(-0.3,0.3)
    else:#上半车道
        vehicle.x = random.uniform(400,900)
        vehicle.y = random.uniform(road.width / 2, road.width)
        vehicle.vx = random.uniform(-40, -30)
        vehicle.vy =  random.uniform(-0.3,0.3)       
    road.add_vehicle(vehicle)
    ID += 1


for t in range(SIMULTION_TIME):
    road.update(TIME_STEP)
    ran = random.randint(0,13)
    if ran % 7 == 0:#每个时刻以1/14的概率添加新车
        vehicle = Vehicle(ID)
        vehicle.lane = random.randint(0,1)
        if vehicle.lane == 1:
            vehicle.x = LONGTH / 2 + random.uniform(-200,200)
            vehicle.y = random.uniform(0, WIDTH * 0.5)
            vehicle.vx = random.uniform(30, 40)
            vehicle.vy =  random.uniform(-0.3,0.3)
        else:
            vehicle.x = LONGTH / 2 + random.uniform(-200,200)
            vehicle.y = random.uniform(WIDTH * 0.5, WIDTH)
            vehicle.vx = random.uniform(-40, -30)
            vehicle.vy =  random.uniform(-0.3,0.3) 
        road.add_vehicle(vehicle)
        ID += 1          


    with open('D:\\网联车\\data\\simulate\\{}s.csv'.format(t),'w',newline='') as fi:
        writer = csv.writer(fi)
        writer.writerow(['t','id','x','y','vx','vy','ax','ay','lane'])
        for vehicle in road.vehicles:
            if vehicle.lane == 1:
                writer.writerow([t, vehicle.id, vehicle.x, vehicle.y, vehicle.vx, vehicle.vy, vehicle.ax, vehicle.ay, 'bottom'])
            else:
                writer.writerow([t, vehicle.id, vehicle.x, vehicle.y, vehicle.vx, vehicle.vy, vehicle.ax, vehicle.ay, 'top'])

    # 画图
    x_coords = [vehicle.x for vehicle in road.vehicles]
    y_coords = [vehicle.y for vehicle in road.vehicles]

    plt.scatter(x_coords, y_coords, s=10)

    for vehicle in road.vehicles:
        plt.annotate('{}'.format(vehicle.id), (vehicle.x, vehicle.y))

  

    plt.title('{}th_sec'.format(t))

    plt.savefig('D:\\网联车\\data\\simulate\\figure\\{}th_sec'.format(t))

    plt.close()



