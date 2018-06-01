#!/user/bin/env python3
# _*_ coding: utf-8 _*_

import numpy as np
from MLR import MLR
from PCA import PCA


# 主成分回归
class PCR:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y


# 建模过程，求得主成分回归系数A，PCs为主成分个数
    def computePCs(self):
        # 确定主成分
        Percentage = 0.95
        pca = PCA(self.X)
        U, S, V, compare = pca.SVDdecompose()
        self.kcount = compare.__len__()           # 记录主成分最大数
        comSum = 0
        cSum = sum(compare)
        for i in compare:
            comSum += i
            if comSum / cSum >= Percentage:
                PCs = int(np.where(compare == i)[0][-1]) + 1
                #print("主成分数k: ", PCs)
                self.k = PCs        # 记录符合条件的最佳主成分数
                break

    def model(self, k):
        pca = PCA(self.X)
        U, S, V, compare = pca.SVDdecompose()  # 不可去，会用到计算得到的结果
        # 得到得分矩阵和载荷矩阵
        T, P = pca.PCAdecompose(k)
        #print("得分矩阵T: ", T)
        #print("载荷矩阵P: ", P)
        mlr = MLR(T, self.Y)
        mlr.modelling()
        self.A = np.dot(P, mlr.A)


# 预测过程
    def predict(self, Xnew):
        Ynew = np.dot(Xnew,self.A)
        return Ynew