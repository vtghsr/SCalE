import os
os.environ["OMP_NUM_THREADS"] = '1'
import csv
import pandas as pd
import numpy as np
from AffinityPropagation import dynamic_affinity_propagation
from AffinityPropagation import affinity_propagation
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import SpectralClustering
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from math import dist

# for i in range(13):
#     with open('D:\\网联车\\data\\HighD\\hello_'+str(i)+'.csv','w',newline='') as fi:
#         writer = csv.writer(fi)
#         writer.writerow(['t','id','x','y','vx','vy','ax','ay'])



# with open('D:\\网联车\\data\\HighD\\data\\01_tracks.csv', "r", encoding='utf-8') as f:
#     reader = csv.reader(f)

#     for row in reader:
#         if row[0] == 'frame': # 跳过表头
#             continue
#         # if int(row[1]) > 15:#只观察id为1-15的车
#         #     break 
#         frame = int(row[0])
#         if (frame-1) % 25 == 0 and frame <= 301:
#             t = (frame-1) // 25
#             with open('D:\\网联车\\data\\HighD\\hello_{}.csv'.format(t),'a+',newline='') as fi:
#                 writer = csv.writer(fi)
#                 writer.writerow([str(t),row[1],row[2],row[3],row[6],row[7],row[8],row[9]])

"""对矩阵归一化"""
def normalize(M):
    minM = float('inf')
    maxM = -float('inf')
    n = len(M)
    m = len(M[0])

    for i in range(n):
        for j in range(m):
            if M[i][j] < minM:
                minM = M[i][j]
            if M[i][j] > maxM:
                maxM = M[i][j]

    for i in range(n):
        for j in range(m):
            M[i][j] = (M[i][j]-minM) / (maxM - minM)
    return M

#-------------Affinity Propagation --------------------------
# sim_seq = []
# frame = 1
# while frame <=33:
#     S = [[0 for j in range(6)] for i in range(6)]
#     P = [[0 for j in range(6)] for i in range(6)]
#     V = [[0 for j in range(6)] for i in range(6)]
#     data = []
#     with open('D:\\网联车\\data\\frame_'+str(frame)+'.csv', "r", encoding='utf-8') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if row[0] == 'frame':
#                 continue
#             data.append([float(row[2]),float(row[3]),float(row[4]),float(row[5])])
#     for i in range(6):
#         for j in range(6):
#             P[i][j] = (data[i][0]-data[j][0])**2 +(data[i][1]-data[j][1])**2
#             V[i][j] = (data[i][2]-data[j][2])**2 +(data[i][3]-data[j][3])**2
#     P_nor = normalize(P) # normalize to [0,1]
#     V_nor = normalize(V)

#     for i in range(6):
#         for j in range(6):
#             S[i][j] = -0.8 * P_nor[i][j] -0.2 * V_nor[i][j]
 

#     sim_seq.append(S)
#     frame += 1
# sim_seq = np.array(sim_seq)


        


# cluster_centers_indices, labels= dynamic_affinity_propagation(sim_seq,preference=-0.05,verbose=True,return_n_iter=False)
# print(cluster_centers_indices,labels)


# cluster_centers_indices, labels= affinity_propagation(sim_seq[14],preference=-0.05,return_n_iter=False,)
# print(cluster_centers_indices,labels)

# af = AffinityPropagation(preference=-0.05,affinity='precomputed')
# af.fit(sim_seq[0])
# print(af.cluster_centers_indices_)
# print(af.labels_)


#---------------------------------------------------------------------------------------------------------
# Spectral Clustering

A_seq = []
frame = 0
while frame <=6:
    data = []
    with open('D:\\网联车\\data\\simulate\\{}s.csv'.format(frame), "r", encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == 't':
                continue
            data.append([float(row[2]),float(row[3]),float(row[4]),float(row[5])])
    n = len(data) 
    A = [[0 for j in range(n)] for i in range(n)]
    P = [[0 for j in range(n)] for i in range(n)]
    V = [[0 for j in range(n)] for i in range(n)]
    alpha = 0.5 # 位置相似度权重
    beta = 0.5  # 速度相似度权重
    for i in range(n):
        for j in range(n):
            if i == j:
                A[i][j] = 1
                continue
            P[i][j] = dist((data[i][0],data[i][1]),(data[j][0],data[j][1]))
            if P[i][j] > 180:
                A[i][j] = 0
                continue
            V[i][j] = dist((data[i][2],data[i][3]),(data[j][2],data[j][3]))
            P[i][j] = 1 / P[i][j]
            V[i][j] = 1 / V[i][j]
            A[i][j] = alpha * P[i][j] + beta * V[i][j]

    A = normalize(A)
    A_seq.append(A)
    frame += 1



n_clusters = 4
sc = SpectralClustering(n_clusters,affinity='precomputed')
labels = sc.fit_predict(A_seq[1])

res = [[] for i in range(n_clusters)]
for id,lab in enumerate(labels):
    res[lab].append(id)
print(res)

# 求CH
eigenvalues, eigenvectors = np.linalg.eig(A_seq[3])
max_value, max_index = eigenvalues[0], 0
for i,v in enumerate(eigenvalues):
    if v > max_value:
        max_value, max_index = v, i

centrality = eigenvectors[:,max_index]
sign = 1 if centrality[0] > 0 else -1
for c in centrality:
    assert c * sign > 0
if sign == -1:
    centrality = [-1 * c for c in centrality]
CHs = []
for clustering in res:
    max_c, max_id = centrality[clustering[0]], clustering[0]
    for id in clustering:
        if centrality[id] > max_c:
            max_c, max_id = centrality[id], id
    CHs.append(max_id)
print(CHs)

    
    


