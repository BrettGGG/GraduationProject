#!/user/bin/env python3
# _*_ coding: utf-8 _*_


'a test module'

__author__ = "Brett"

import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
# 配置中文显示
zhfont1 = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')

# matlab文件名
matfn = u'F:\PyCharm\GraduationProject\corn.mat'
data = sio.loadmat(matfn)


# get data from matlabobject in .mat file
def getdata (m):
    return np.array(m.__getitem__("data")[0][0])

m5s = data['m5spec']
mp5s = data['mp5spec']
mp6s = data['mp6spec']
propvals = data['propvals']
m5nbs = data['m5nbs']
mp5nbs = data['mp5nbs']
mp6nbs = data['mp6nbs']

# 返回数据数组
m5sArray, mp5sArray, mp6sArray, propvalsArray, m5nbsArray, mp5nbsArray, mp6nbsArray \
= map(getdata, [m5s, mp5s, mp6s, propvals, m5nbs, mp5nbs, mp6nbs])

# 画出光谱
x = np.arange(1100,2500,2)
for j in range(0,m5sArray.shape[0]):
    y = m5sArray[j,:]
    plt.plot(x,y,'b')

plt.xlabel("波长 (nm)",fontproperties=zhfont1)
plt.ylabel("吸光度 (AU)",fontproperties=zhfont1)
plt.title("80组玉米样本光谱",fontproperties=zhfont1)
plt.show()

for j in range(0,3):
    y = m5sArray[j,:] + 0.5*j  # 源机光谱
    plt.plot(x,y,'r')
    y = mp5sArray[j,:] + 0.5*j   # 目标机光谱
    plt.plot(x, y, 'b')

plt.xlabel("波长 (nm)",fontproperties=zhfont1)
plt.ylabel("吸光度 (AU)",fontproperties=zhfont1)
plt.title("仪器m5上测量的3组玉米样本光谱",fontproperties=zhfont1)
plt.show()



#import numpy as np
import PCR
#Rms = np.arange(24).reshape(4,6)
#Rss = np.arange(1,25).reshape(4,6)
# 取前 3 组样本
Rms = m5sArray[0:3, :]
Rss = mp5sArray[0:3, :]

win = 1
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
    pcr = PCR.PCR(X[i], Rms[:, i])
    pcr.model()    # 建模
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
    zeroL = np.zeros(col -1 -i)
    Ft.append(np.hstack((zeroL, B[col - 1 - i], zeroR)))
F = np.array(Ft).T
#Rssun = np.arange(2,26).reshape(4,6)
#Rmsunt = np.dot(Rssun, F)
#print (Rmsunt)

Rssun = mp5sArray[0:3, :]
Rmsun = m5sArray[0:3, :][:, win: Rssun.shape[1]-win]
for j in range(0,3):
    Rmsyuce = np.dot(Rssun, F)
    # 舍弃窗口两端
    xwin = x[win: Rssun.shape[1]-win]
    y = Rmsyuce[j, :] - 0.5*j  # 预测值
    plt.plot(xwin, y,'r')
    y = Rmsun[j, :] - 0.5 * j   #真实值
    plt.plot(xwin, y, 'b')

plt.xlabel("波长 (nm)",fontproperties=zhfont1)
plt.ylabel("吸光度 (AU)",fontproperties=zhfont1)
plt.title("根据仪器m5上预测的3组玉米样本光谱",fontproperties=zhfont1)
plt.show()