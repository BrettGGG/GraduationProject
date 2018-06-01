#!/user/bin/env python3
# _*_ coding: utf-8 _*_


'a test module'

__author__ = "Brett"
import math
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


# 计算平均光谱
def averSpec(R):
    # 若只有一个样本，则平均光谱就为R
    if R.shape[0] == R.size:
        return R
    else :
        return np.mean(R,0)

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
    plt.plot(x,y,'r',label = '样本'+str(j)+ '(Master)')
    y = mp5sArray[j,:] + 0.5*j   # 目标机光谱
    plt.plot(x, y, 'b',label =  '样本'+str(j)+ '(Slaver)')
plt.legend(prop=zhfont1)

plt.xlabel("波长 (nm)",fontproperties=zhfont1)
plt.ylabel("吸光度 (AU)",fontproperties=zhfont1)
plt.title("两台仪器3组玉米样本光谱对比",fontproperties=zhfont1)
plt.show()



#import numpy as np
import PDS
import Shenks

# 取前 3 组样本
Rms = m5nbsArray[0:3, :]
Rss = mp5nbsArray[0:3, :]
pds = PDS.PDS(Rms, Rss)
# 窗口大小选择
win = 1
k = 1
pds.model(win,k)

Rssun = mp5nbsArray[0:3, :]
Rmsun = m5nbsArray[0:3, :][:, win: Rssun.shape[1]-win]

Rssyuce = pds.predict(Rssun)
# 舍弃窗口两端
xwin = x[win: Rssun.shape[1]-win]
#y1 = averSpec(Rmsyuce) # 预测值
#plt.plot(xwin, y1,'r')
#    y = Rmsun[j, :] - 0.5 * j   #真实值
#    plt.plot(xwin, y, 'b')
y2 = averSpec(Rms)[win: Rssun.shape[1]-win]   # 平均光谱
plt.plot(xwin, y2, 'b', label = '平均光谱')
# 差值
for i in range(3):
    plt.plot(xwin , Rssyuce[i, :] - y2 ,label = '样本'+str(i)+ '与平均光谱差值')



plt.xlabel("波长 (单位：nm)",fontproperties=zhfont1)
plt.ylabel("吸光度 (单位：AU)",fontproperties=zhfont1)
plt.title("根据仪器m5上预测的3组玉米样本光谱",fontproperties=zhfont1)
plt.legend(prop=zhfont1)
plt.show()

shenks = Shenks.Shenks(Rms,Rss)
shenks.model()
xnew = shenks.xnew   # 由一元二次模型校正后的波长
ynew = shenks.ynew   # 由校正后波长插值后的吸光度

# 拟合前后的图像
for i in range(Rms.shape[0]):
    plt.plot(xnew, ynew[i], label='slinear' + str(i))
    plt.plot(x, y, label='originline' + str(i))
plt.legend()
plt.show()

Rssyuce = shenks.predict(Rssun)
xnew = shenks.xnew   # 由校正模型  校正后的 波长
plt.plot(xwin, y2, 'b', label='averageSpectrum')
plt.legend()
# 差值
y2 = y2[:xnew.shape[0]]
for i in range(Rssun.shape[0]):
    plt.plot(xnew, Rssyuce[i] - y2, label='predictoffset' + str(i))
    plt.legend()
plt.show()


