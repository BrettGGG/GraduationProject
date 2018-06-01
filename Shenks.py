#!/user/bin/env python3
# _*_ coding: utf-8 _*_

"专利算法"

import numpy as np
import math
from scipy import interpolate

# 求乘积之和
def multipl(a, b):
    sumofab = 0.0
    for i in range(len(a)):
        temp = a[i] * b[i]
        sumofab += temp
    return sumofab


# 求皮尔逊相关系数
def corrcoef(x, y):
    n = len(x)
    # 求和
    sum1 = sum(x)
    sum2 = sum(y)
    # 求乘积之和
    sumofxy = multipl(x, y)
    # 求平方和
    sumofx2 = sum([pow(i, 2) for i in x])
    sumofy2 = sum([pow(j, 2) for j in y])
    num = sumofxy - (float(sum1) * float(sum2) / n)
    # 计算皮尔逊相关系数
    den = math.sqrt((sumofx2 - float(sum1 ** 2) / n) * (sumofy2 - float(sum2 ** 2) / n))
    return num / den

'''
    # 一元二次抛物线建模过程
def x2model(x, y):
    A = np.array([1, x, x * x])
    B = np.array(y)
    return np.linalg.solve(A, B)  # 返回三个系数a,b,c; y = a+bx+cx^2

    # 一元二次抛物线模型求解过程
def getYfromx2model(*a, x):
    return a[0] + a[1] * x + a[2] * x * x
'''



class Shenks:
    def __init__(self, Rms, Rss):   # Rms 为源机样本光谱，Rss为目标机样本光谱
        self.Rms = Rms
        self.Rss = Rss


    def model(self,win = 1):
        Rms = self.Rms
        Rss = self.Rss
        self.win = win
        # 循环计算相关系数
        X = []
        # 若只有一个样本，即Rss为一维时增加一维
        if Rss.shape[0] == Rss.size:
            Rss = np.array([Rss])
        for i in range(win, Rss.shape[1] - win):
            X.append(Rss[:, i - win: i + win + 1])
        X = np.array(X)
        self.X = X
        #        # 舍弃窗口两端,关联Rmsi 与Xi
        #        Rms = Rms[:, win: Rms.shape[1] - win]

        corr = []
        l = []  # 存放Rss 与Rmsi 相关系数最大的波长点
        for i in range(X.shape[0]):
            for j in range(X.shape[2]):
                # Rmsi 与 Rssi-j,...Rssi+k-1,Rssi+k+1 的相关系数
                corr.append(corrcoef(Rms[:, i], X[i][:, j]))
            l.append(corr.index(max(corr)) + i)  # 转换到全波长索引
            corr = []

        irss = []  # 存储与源机波长i 相同的波长 i'
        count = 0   # 记录  范围内的X 数目
        for i in range(X.shape[0]):
            if l[i] - 1 < 0:      # 不计算超出范围的边缘波长
                continue
            if l[i]+2 >= Rms.shape[1]:
                continue
            count = count + 1
            corr = []
            for j in range(l[i] - 1, l[i] + 2):
                corr.append(corrcoef(Rms[:, j], Rss[:, j]))
            # 建立 波长与相关系数的抛物线模型
            r = np.polyfit([l[i] - 1, l[i], l[i] + 1], corr, 2)
            p = np.poly1d(r)
            pj = [p(j) for j in range(l[i] - 1, l[i] + 2)]
            irss.append(pj.index(max(pj)) + l[i] - 1)
        self.count = count

        # 建立一元二次抛物线波长校正模型
        i1 = np.polyfit(range(count), irss, 2)
        self.pi1 = np.poly1d(i1)
        '''
        #  拟合波长与吸光度曲线
        # 第1個擬合，自由度為20
        z1 = np.polyfit(x, y, 20)
        # 生成的多項式對象
        p1 = np.poly1d(z1)
        print(z1)
        print(p1)

        # 第2個擬合，自由度為30
        z2 = np.polyfit(x, y,30)
        # 生成的多項式對象
        p2 = np.poly1d(z2)
        print(z2)
        print(p2)

        # 原曲線
        plt.plot(x, y, 'b-', label='Origin Line')
        # 自由度為20，30 的曲線
        plt.plot(x, p1(x), 'g-', label='Poly Fitting Line(deg=20)')
        plt.plot(x, p2(x), 'r*', label='Poly Fitting Line(deg=30)')
        plt.legend()
        plt.show()
        '''

        Rms = Rms[:, win: Rms.shape[1] - win]

        x = range(1100, 1100 + X.shape[0] * 2, 2)

        # 若只有一个样本，即Rms为一维时增加一维
        if Rms.shape[0] == Rms.size:
            Rms = np.array([Rms])

        ynew = []
        xnew = np.array([])
        for i in range(Rms.shape[0]):
            y = Rms[i]
            xnew = np.array(irss) * 2 + 1100
            xnew = xnew[0: np.where(xnew <= X.shape[0] * 2 - 2 + 1100)[0].shape[0]]  # 截取范围内的波长
            f = interpolate.interp1d(x, y, kind='slinear')
            ynew.append(f(xnew))
            self.xnew = xnew
            self.ynew = ynew
#            plt.plot(xnew, ynew[i] + 0.01, label='slinear' + str(i))
#            plt.plot(x, y, label='originline' + str(i))
#            plt.legend()
#        plt.show()
        ynew = np.array(ynew)
        from MLR import MLR
        mlr = MLR(ynew, Rms[:, 0:xnew.shape[0]])
        mlr.modelling()
        self.A = mlr.A



    def predict(self,Rssun):
        # 波长校正
        xnew = self.xnew
        pi1 = self.pi1   # 建立的一元二次抛物线模型
        win = self.win    # 窗口大小
        X = self.X
        issun = np.array([pi1(i) for i in range(1100, X.shape[0] * 2 + 1100, 2)])
        # 插值计算
        x = range(1100, 1100 + X.shape[0] * 2, 2)
        ynew = []

        for i in range(Rssun.shape[0]):
            y = Rssun[i, win: Rssun.shape[1] - win]
            xnew = issun[(issun >= 1100)&(issun <= X.shape[0] * 2-win*2  + 1100)]  # 截取范围内的波长
            f = interpolate.interp1d(x, y, kind='slinear')
            ynew.append(f(xnew))
        ynew = np.array(ynew)
            # 预测结果
        A = self.A
        mins = min(A.shape[0],ynew.shape[1])     # 同步  步长
        A = A[:mins, :mins]
        ynew = ynew[:,:mins]
        xnew = xnew[:mins]
        self.xnew = xnew
        self.ynew = ynew
        self.A = A
        Rssyuce = np.dot(ynew, A)
        return Rssyuce



