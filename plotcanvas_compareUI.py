#!/user/bin/env python3
# _*_ coding: utf-8 _*_


'DS 算法界面的逻辑实现部分'

__author__ = "Brett"

from PyQt5.QtWidgets import *
from compareUI import Ui_CompareDialog
import numpy as np
from plotcanvas import PlotCanvas
from MLR import MLR   # DS算法
from PDS import PDS   # PDS算法
from Shenks import Shenks  # Shenks算法

class myComDialog(QDialog, Ui_CompareDialog):
    def __init__(self, data, parent = None):
        super(myComDialog, self).__init__(parent)
        self.setupUi(self)
        self.data = data
        # 全样本光谱
        self.Rms = None
        self.Rss = None
        # 部分样本光谱
        self.Rm = None
        self.Rs = None

        self.n = 3 # 默认截取样本数量
        self.win = 1 # 默认窗口大小
        self.k = 1 # 默认主成分数
        # 绑定事件
        self.cbx1.currentIndexChanged.connect(self.on_cbx1changed)
        self.cbx2.currentIndexChanged.connect(self.on_cbx2changed)
        self.btn.clicked.connect(self.plot)


    def on_cbx1changed(self):
        data = self.data
        if self.cbx1.currentIndex()== 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个master样品集!"))
            return
        matdata = data[self.cbx1.currentText()]
        self.Rms = np.array(matdata.__getitem__("data")[0][0])
        pass

    def on_cbx2changed(self):
        data = self.data
        if self.cbx2.currentIndex()== 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个slaver样品集!"))
            return
        if self.cbx1.currentIndex()== 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个master样品集!"))
            return
        if self.cbx2.currentIndex() == self.cbx1.currentIndex():
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个与主机不同的slaver样品集!"))
            return

        matdata = data[self.cbx2.currentText()]
        self.Rss = np.array(matdata.__getitem__("data")[0][0])
        pass


    def plot(self):
        QMessageBox.information(self,"tip","正在绘制请稍后...")
        self.Rm = self.Rms[:self.n, :]  # 截取前n 个样本
        self.Rs = self.Rss[:self.n, :]
        self.plotDS()
        self.plotPDS()
        self.plotShenks()

    def plotDS(self):
        p = PlotCanvas()
        mlr = MLR(self.Rs, self.Rm)  # 由选取的n 组样本进行DS 建模
        mlr.modelling()
        Rsun = self.Rss[0:self.n, :] # 选取子机上同样n 组未知样本进行DS 预测
        Rsunp = np.dot(Rsun, mlr.A) # A 为得到的转换矩阵，Rsunp 为预测结果
        x = np.arange(1100, 2500, 2)
        y1 = p.averSpec(self.Rms)  # 源机均值光谱
        p.axes.plot(x, y1, 'r-', label="源机均值光谱")
        for i in range(Rsunp.shape[0]):
            y2 = Rsunp[i]  # 从子机预测的光谱
            p.axes.plot(x, y2)
            # 差值
            y = y2 - y1   # 目标机光谱
            p.axes.plot(x, y)
        p.axes.legend()
        p.axes.set_title("DS算法预测结果")
        self.hlayout4.replaceWidget(self.wg1, p)
        self.wg1 = p
        Rmun = self.Rms[0:self.n, :]
        sep = p.computeSEP(Rmun, Rsunp)
        self.lb5.setVisible(True)
        self.lb5.setText('%.5f'% sep)
        pass

    def plotPDS(self):
        pds = PDS(self.Rm, self.Rs)
        pds.model(self.win)  # 以默认值计算,得到最佳的K
        pds.model(self.win, pds.k)   # 以最佳K pds 建模 得到pds.F
        Rsun = self.Rss[0:self.n, :]  # 选取子机上同样n 组未知样本进行PDS 预测
        Rsunp = pds.predict(Rsun)  # Rsunp 为预测结果
        win = self.win
        # 舍弃窗口两端
        Rmswin = self.Rms[:, win: Rsun.shape[1] - win]  #Rmswin 源机上去掉两端的光谱
        x = np.arange(1100, 2500, 2)
        xwin = x[win: Rsun.shape[1] - win]
        p = PlotCanvas()
        # 差值
        y1 = p.averSpec(Rmswin)  # 源机均值光谱
        p.axes.plot(xwin, y1, 'r-', label="源机均值光谱")
        for i in range(Rsunp.shape[0]):
            y2 = Rsunp[i]  # 从子机预测的光谱
            p.axes.plot(xwin, y2)
            # 差值
            y = y2 - y1   # 目标机光谱
            p.axes.plot(xwin, y)
        p.axes.legend()
        p.axes.set_title("PDS算法预测结果")
        self.hlayout4.replaceWidget(self.wg2, p)
        self.wg2 = p
        Rmun = Rmswin[0:self.n, :]
        sep = p.computeSEP(Rmun, Rsunp)
        self.lb6.setVisible(True)
        self.lb6.setText('%.5f' % sep)
        pass


    def plotShenks(self):
        win = self.win
        sks = Shenks(self.Rm, self.Rs)
        # 窗口大小选择
        sks.model(win)  # sks 建模
        xnew = sks.xnew  # 由一元二次模型校正后的波长
        ynew = sks.ynew  # 由校正后波长插值后的吸光度
        Rsun = self.Rss[0:self.n, :]  # 选取子机上同样n 组未知样本进行Sks预测
        Rsunp = sks.predict(Rsun)
        x = np.arange(1100, 2500, 2)
        # 舍弃窗口两端
        xnew = sks.xnew  # 由校正模型  校正后的 波长
        Rmswin = self.Rms[:, win: Rsun.shape[1] - win]

        p = PlotCanvas()
        y1 = p.averSpec(Rmswin)  # 源机均值光谱
        y1 = y1[:xnew.shape[0]]  # Rmswin 源机上去掉多余波长的光谱
        # 差值
        p.axes.plot(xnew, y1, 'r-',label = "源机均值光谱")
        for i in range(Rsunp.shape[0]):
            y2 = Rsunp[i]  # 从子机预测的光谱
            p.axes.plot(xnew, y2)
            # 差值
            y = y2 - y1  # 目标机光谱
            p.axes.plot(xnew, y)
        p.axes.legend()
        p.axes.set_title("Shenk's算法预测结果")
        self.hlayout4.replaceWidget(self.wg3, p)
        self.wg3 = p

        Rmswin = Rmswin[:, :xnew.shape[0]]
        Rmun = Rmswin[0:self.n, :]
        sep = p.computeSEP(Rmun, Rsunp)
        self.lb7.setVisible(True)
        self.lb7.setText('%.5f' % sep)
        pass




