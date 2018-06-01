#!/user/bin/env python3
# _*_ coding: utf-8 _*_

import numpy as np
from PCR import PCR


# 分段直接校正算法
class PDS:
    def __init__(self, Rms, Rss):   # Rms 为源机样本光谱，Rss为目标机样本光谱
        self.Rms = Rms
        self.Rss = Rss


#  建模过程，计算转换矩阵F, win 为选择的窗口大小
    def model(self, win = 1, k=1):
        Rms = self.Rms
        Rss = self.Rss
        # 循环计算转换系数
        X = []
        # 若只有一个样本，即Rss为一维时增加一维
        if Rss.shape[0] == Rss.size:
            Rss = np.array([Rss])
        for i in range(win, Rss.shape[1] - win):
            X.append(Rss[:, i - win: i + win + 1])
        X = np.array(X)
        # 舍弃窗口两端,关联Rmsi 与Xi
        Rms = Rms[:, win: Rms.shape[1] - win]
        # 转换系数矩阵B
        B = []
        for i in range(X.shape[0]):
            pcr = PCR(X[i], Rms[:, i])
            pcr.computePCs()
            self.kcount = pcr.kcount  # 记录主成分最大数
            self.k = pcr.k  # 记录符合条件的最佳主成分数
            pcr.model(k)  # 建模

            B.append(pcr.A)
        #  size  698 * 3
        B = np.array(B)
        # 转置
        Bt = B.T
        # 形成带状对角矩阵
        row = Bt.shape[0]
        col = Bt.shape[1]
        Ft = []
        for i in range(col - 1, -1, -1):
            zeroR = np.zeros(i)
            zeroL = np.zeros(col - 1 - i)
            Ft.append(np.hstack((zeroL, B[col - 1 - i], zeroR)))
        self.F = np.array(Ft).T

# 预测过程
    def predict(self, Xnew):
        Ynew = np.dot(Xnew,self.F)
        return Ynew

