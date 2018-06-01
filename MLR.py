#!/user/bin/env python3
# _*_ coding: utf-8

import numpy as np


# 多元线性回归（最小二乘法）
class MLR:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.A = None

# Y=XA，建模过程，求得回归系数A
    def modelling(self):
        X = self.X
        Y = self.Y
        Xt = np.transpose(X)
        XtX = np.dot(Xt, X)
        XtXinv = np.linalg.pinv((XtX))
        temp = np.dot(XtXinv, Xt)
        A = np.dot(temp,Y)
        self.A = A
        #print (A.shape)


# 预测过程，求对应Y
    def predict(self, X):
         Y = np.dot(X,self.A)
         return Y

