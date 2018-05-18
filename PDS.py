#!/user/bin/env python3
# _*_ coding: utf-8 _*_

import numpy as np
from PCR import PCR


# 分段直接校正
class PDS:
    def __init__(self, Rms, Rss):   # Rms 为源机样本光谱，Rss为目标机样本光谱
        self.Rms = Rms
        self.Rss = Rss


# 计算转换系数矩阵B
    def getTrans(self):
        Rms = self.Rms
        Rss = self.Rss
        # 窗口大小选择
        win = 1
        # 循环计算转换系数
        X = []
        # 若只有一个样本，即Rss为一维时增加一维
        if Rss.shape[0] == Rss.size:
            Rss = np.array([Rss])
        for i in range(win, Rss.shape[1] - win):
            X.append(Rss[:, i - win : i + win+1])
        X = np.array(X)

        # 转换系数矩阵B
        B = []
        for Xi in X:
            pcr = PCR(self.Rms, self.Xi)
            compare = pcr.confirmPCs()  # 确定主成分数
            print("相邻特征值比值:\n", compare)
            k = int(input("请输入主成分数k: "))
            pcr.model(k)
            B.append(pcr.A)

# 将B中的每个矩阵投影至一个方向
        B = B[:,:,0]



