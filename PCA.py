#!/user/bin/env python3
# _*_ coding: utf-8 _*_

import numpy as np


# 主成分分析
class PCA:
    def __init__(self, X):
        self.X = X      # 分析矩阵
        self.T = None  # 得分矩阵
        self.P = None  # 载荷矩阵


# SVD（奇异值分解）B = USV* ,
    def SVDdecompose(self):
        B = np.linalg.svd(self.X, full_matrices=False)
        U = B[0]
        lamda = B[1]   # 奇异值数组，降序排列
        V = B[2]
        i = len(lamda)
        S = np.zeros((i, i))
        S = np.diag(lamda)
        self.T = np.dot(U, S)  # 得分矩阵
        V = V.T
        self.P = V      # 载荷矩阵
        compare = []   # 奇异值比值列表
        for i in range(len(lamda)-1):
            temp  = lamda[i]/lamda[i+1]
            compare.append(temp)
        return U, S, V, compare

# 由 特征值比值列表确定主成分个数k，确定最后的得分矩阵T 和载荷矩阵P
    def PCAdecompose(self, k):
        T = self.T[:, :k]
        P = self.P[:, :k]
        return T, P

