import csv 
from math import dist
from typing import List,Set


R = 180
nodes = {}
RSU_x = [(i * 200) for i in range(21)]
RSU_y = 100
class Node:
    def __init__(self,id,x,y,vx,vy) -> None:
        self.id, self.pos, self.vel = int(id), (float(x),float(y)), (float(vx),float(vy))
        self.direction = 1 if self.vel[0] > 0 else -1
        self.neighbors = set([])
        self.selIndex, self.card = -1, 0
        self.CH, self.myCH, self.bkp  = 0, -1, -1 # bkp是备份簇头的id
        self.t = 0 # CH状态有效时限，到t时刻前都有效
    
        
    def update(self,x,y,vx,vy):
        self.pos, self.vel = (float(x),float(y)), (float(vx),float(vy))
    def getCard(self):
        return self.card

def show(nodes,t):
    clusters = {}
    for id,node in nodes.items():
        if node.myCH in clusters:
            clusters[node.myCH].append(id)
        else:
            clusters[node.myCH] = [id,]
    print('result at {}s'.format(t))
    print(clusters)

"""返回输入车辆与最近的RSU的距离"""
def calRsuDis(node):
    pos = node.pos
    for i in range(20):
        if pos[0] >= i * 200 and pos[0] <= (i+1) * 200:
            return min(dist(pos,(i*200,100)),dist(pos,((i+1)*200,100)))


"""更新邻居，计算每个节点的选举指数"""
def calSelIndex():
    for i,node_i in nodes.items():
        rel_mob, rel_dis = [], []
        for j,node_j in nodes.items():
            if i == j:
                continue
            if dist(node_i.pos,node_j.pos) <= R:#j是i的邻居
                node_i.neighbors.add(j)
                rel_mob.append(dist(node_i.vel,node_j.vel))
                rel_dis.append(dist(node_i.pos,node_j.pos))
            else:#j不是i的邻居
                if j in node_i.neighbors:
                    node_i.neighbors.remove(j)
        tmp = [j for j in node_i.neighbors if j in nodes] # 提出i的邻居中已经离开系统的点
        node_i.neighbors = set(tmp)
        N = len(node_i.neighbors)
        if N != 0:
            node_i.selIndex = sum(rel_mob) / (N * max(rel_mob)) + sum(rel_dis) / (N * max(rel_dis)) 
        else:
            node_i.selIndex = 0

"""选备份簇头"""
def calBackup(clusters):
    for ch_id in clusters:
        if len(clusters[ch_id]) == 1:# 只有一个节点的集群，没有备份簇头
            nodes[ch_id].bkp = -1
            continue
        avg_index = 0
        for cm_id in clusters[ch_id]:
            if cm_id == ch_id:
                continue
            nodes[cm_id].card = len(nodes[cm_id].neighbors.intersection(clusters[ch_id]))
            avg_index += nodes[cm_id].selIndex
        Ac = list(clusters[ch_id])
        Ac = sorted(Ac,key=lambda a:nodes[a].card,reverse=True)
        avg_index = avg_index / (len(Ac) - 1)
        bkp = -1
        for cm_id in Ac:
            if cm_id == ch_id:# 备份CH和CH不要相同
                continue
            if nodes[cm_id].selIndex <= avg_index:
                bkp = cm_id
                break
        for cm_id in Ac:
            nodes[cm_id].bkp = bkp 

"""更新nodes"""
def readNodes(t):
    with open('D:\\网联车\\data\\simulate\\{}s.csv'.format(t), "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        id_list, x_list, y_list, vx_list, vy_list = [], [], [], [], []
        for row in reader:
            id_list.append(int(row['id']))
            x_list.append(float(row['x']))
            y_list.append(float(row['y']))
            vx_list.append(float(row['vx']))
            vy_list.append(float(row['vy']))
        global nodes
        new_nodes = {}
        for i in range(len(id_list)): 
            id, x, y, vx, vy = id_list[i], x_list[i], y_list[i], vx_list[i], vy_list[i]
            if id not in nodes:#新添加的点
                new_nodes[id] = Node(id,x,y,vx,vy)
            else:
                nodes[id].update(x,y,vx,vy)
                new_nodes[id] = nodes[id]
        nodes = new_nodes

"""获取当前集群状态"""
def getClusters():
    clusters = {}
    for i, node_i in nodes.items():
        if node_i.myCH in clusters:
            clusters[node_i.myCH].add(i)
        else:
            clusters[node_i.myCH] = set([i,])
    return clusters
def maintenance(t):

    # t-1时刻聚类结果
    clusters = getClusters()
    old_N = len(nodes)
    bkp_table = {}
    for ch_id in clusters:
        bkp_table[ch_id] = nodes[ch_id].bkp

    # 读取t时刻的节点
    readNodes(t)

    # 新节点进入系统，选举
    if len(nodes) > old_N:
        election(t)
        return

    #CH离开系统，备份簇头成为CH
    for ch_id in clusters:
        if ch_id not in nodes:
            if bkp_table[ch_id] == -1: # 没有备份簇头，重新选举
                election(t)
                return
            for cm_id in clusters[ch_id]:
                if cm_id == bkp_table[ch_id]:
                    nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 1, cm_id, -1
                else:
                    nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 0, bkp_table[ch_id], -1
    
    clusters = getClusters()
    while len(clusters) != 0:
        first_ch = -1
        for ch_id in clusters:
            first_ch = ch_id
            break
        second_ch = -1
        for ch_id in clusters:
            if first_ch != ch_id and dist(nodes[first_ch].pos,nodes[ch_id].pos) <= R:
                second_ch = ch_id
                break
        if second_ch == -1: # first_ch和任意其他CH的距离都>R，
            clusters.pop(first_ch)
        else:
            first_bkp, second_bkp = nodes[first_ch].bkp, nodes[second_ch].bkp
            # first_ch与second_ch距离<=R，但first_bkp与second_ch距离>R，first_bkp成为簇头
            if first_bkp != -1 and dist(nodes[first_bkp].pos,nodes[second_ch].pos) > R:
                for cm_id in clusters[first_ch]:
                    if cm_id == first_bkp:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 1, first_bkp, -1
                    else:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 0, first_bkp, -1
                clusters[first_bkp] = clusters.pop(first_ch)
            # first_ch与second_ch距离<=R，但first_ch与second_bkp距离>R，second_bkp成为簇头
            elif second_bkp != -1 and dist(nodes[first_ch].pos,nodes[second_bkp].pos) > R:
                for cm_id in clusters[second_ch]:
                    if cm_id == nodes[second_ch].bkp:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 1, second_bkp, -1
                    else:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 0, second_bkp, -1
                clusters[second_bkp] = clusters.pop(second_ch)
            # first_ch与second_ch距离<=R，但first_bkp与second_bkp距离>R，first_bkp\second_bkp成为簇头
            elif first_bkp != -1 and second_bkp != -1 and dist(nodes[first_bkp].pos,nodes[second_bkp].pos) > R:
                for cm_id in clusters[first_ch]:
                    if cm_id == first_bkp:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 1, first_bkp, -1
                    else:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 0, first_bkp, -1
                clusters[first_bkp] = clusters.pop(first_ch)
                for cm_id in clusters[second_ch]:
                    if cm_id == second_bkp:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 1, second_bkp, -1
                    else:
                        nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 0, second_bkp, -1
                clusters[second_bkp] = clusters.pop(second_ch)
            # 合并first\second集群
            else:
                first_cms, second_cms = clusters.pop(first_ch), clusters.pop(second_ch)
                if len(first_cms) > len(second_cms):
                    for cm_id in first_cms.union(second_cms):
                        if cm_id == first_ch:
                            nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 1, first_ch, -1
                        else:
                            nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 0, first_ch, -1
                    clusters[first_ch] = first_cms.union(second_cms)
                else:
                    for cm_id in first_cms.union(second_cms):
                        if cm_id == second_ch:
                            nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 1, second_ch, -1
                        else:
                            nodes[cm_id].CH, nodes[cm_id].myCH, nodes[cm_id].bkp = 0, second_ch, -1
                    clusters[second_ch] = first_cms.union(second_cms)

    clusters = getClusters()
    # CM不在CH的范围了，选举（维护完后发现还是有CM断联，只能重新选举）
    for ch_id in clusters:
        for cm_id in clusters[ch_id]:
            if dist(nodes[ch_id].pos,nodes[cm_id].pos) > R:
                election(t)
                return
    # 更新时间戳    
    for i in nodes:
        nodes[i].t += 1



def election(t):
    print('election at {}s'.format(t))
    readNodes(t)
    calSelIndex()
    # 每个节点和邻居比较选举指数，选举指数最小的为CH
    for i, node_i in nodes.items():
        N = len(node_i.neighbors)
        if (N !=0 and node_i.selIndex <= min([nodes[j].selIndex for j in node_i.neighbors])\
            or N == 0)\
                and node_i.t == t:# 选择指数是邻居中最小的或没有邻居，为CH
            node_i.CH, node_i.myCH = 1, i
            node_i.t += 1
            for j in node_i.neighbors:
                if nodes[j].t == t: # j还没有被划入别的集群
                    nodes[j].CH, nodes[j].myCH = 0, i
                    nodes[j].t += 1
    for i,node_i in nodes.items():
        if node_i.t == t: # 选择指数不是邻居中最小的，但是邻居中没有CH
            node_i.CH, node_i.myCH = 1, i
            node_i.t += 1
    # for i,node_i in nodes.items():#确保每个节点都被遍历了
    #     assert node_i.t == t + 1

    # 聚类结果
    clusters = {}
    for i, node_i in nodes.items():
        if node_i.myCH in clusters:
            clusters[node_i.myCH].add(i)
        else:
            clusters[node_i.myCH] = set([i,])
    # 选备份簇头
    calBackup(clusters)
        


    

def scale():
    t = 0
    election(t)
    election(t+1)
    show(nodes,t)
    while t <= 15:
        t += 1
        maintenance(t)
        show(nodes,t)
            
if __name__ == "__main__":
    scale()

            

