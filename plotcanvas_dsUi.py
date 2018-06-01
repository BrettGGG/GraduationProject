#!/user/bin/env python3
# _*_ coding: utf-8 _*_


'DS 算法界面的逻辑实现部分'

__author__ = "Brett"

from PyQt5.QtWidgets import *
from dsUI import Ui_DsDialog
import numpy as np
from plotcanvas import PlotCanvas
from MLR import MLR   # DS算法

class myDsDialog(QDialog, Ui_DsDialog):
    def __init__(self, data, parent = None):
        super(myDsDialog, self).__init__(parent)
        self.setupUi(self)
        self.data = data
        # 全样本光谱
        self.Rms = None
        self.Rss = None
        # 部分样本光谱
        self.Rm = None
        self.Rs = None

        self.n = 3 # 默认截取样本数量
        # 绑定事件
        self.cbx1.currentIndexChanged.connect(self.on_cbx1changed)
        self.cbx2.currentIndexChanged.connect(self.on_cbx2changed)
        self.cbx3.currentIndexChanged.connect(self.on_cbx3changed)
        self.btn0.clicked.connect(self.plotDiff)
        self.btn.clicked.connect(self.plotDS)
        self.btn1.clicked.connect(self.plotSmpAndSep)

    def on_cbx1changed(self):
        data = self.data
        if self.cbx1.currentIndex()== 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个master样品集!"))
            return
        matdata = data[self.cbx1.currentText()]
        self.Rms = np.array(matdata.__getitem__("data")[0][0])
        # 确定样本总数量
        for i in range(80):
            self.cbx3.insertItem(int(i + 1), str(i + 1))
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

    def on_cbx3changed(self):

        if self.cbx3.currentIndex()== 0|\
            self.cbx3.currentIndex() > self.Rms.shape[0]:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择样本数量"))
            return

        self.n = self.cbx3.currentIndex()
        if self.n == 1:
            QMessageBox.information(self, "提示","请选择2个以上样本")
        self.Rm = self.Rms[:self.n, :] # 截取前n 个样本
        self.Rs = self.Rss[:self.n, :]
        QMessageBox.information(self, "提示", "样本数量为："+str(self.Rm.shape[0]))
        pass

    def plotDiff(self):
        p = PlotCanvas()
        x = range(1100, 2500, 2)
        offset = 0.5
        for i in range(self.n):
            y = self.Rm[i, :] + offset * i  # 源机光谱
            p.axes.plot(x, y, label='样本' + str(i+1) + '(Master)')
            y = self.Rs[i, :] + offset * i  # 目标机光谱
            p.axes.plot(x, y,  label='样本' + str(i+1) + '(Slaver)')
        p.axes.legend()
        p.axes.set_title("两台仪器样本光谱对比(offset:"+str(offset)+")")
        self.hlayout4.replaceWidget(self.wg,p)
        self.wg = p
        pass


    def plotDS(self):
        p = PlotCanvas()
        mlr = MLR(self.Rs, self.Rm)  # 由选取的n 组样本进行DS 建模
        mlr.modelling()
        Rsun = self.Rss[:self.n, :] # 选取子机上同样n 组未知样本进行DS 预测
        Rsunp = np.dot(Rsun, mlr.A) # A 为得到的转换矩阵，Rsunp 为预测结果
        x = np.arange(1100, 2500, 2)
        for i in range(Rsunp.shape[0]):
            y1 = p.averSpec(self.Rms) # 源机均值光谱
            p.axes.plot(x, y1, 'r-', label='源机均值光谱')
            y2 = Rsunp[i, :]  # 从子机预测的光谱
            p.axes.plot(x, y2, label='样本' + str(i + 1) + '预测值')
            # 差值
            y = y2 - y1   # 目标机光谱
            p.axes.plot(x, y, label='样本' + str(i + 1) + '预测偏差')
        p.axes.legend()
        p.axes.set_title("DS算法预测结果")
        self.hlayout4.replaceWidget(self.wg, p)
        self.wg = p
        Rmun = self.Rms[:self.n, :]
        sep = p.computeSEP(Rmun, Rsunp)
        self.lb5.setVisible(True)
        self.lb5.setText('%.5f'% sep)
        pass

    def plotSmpAndSep(self):
        self.lb5.setVisible(False)
        p = PlotCanvas()
        sep = []
        self.lb4.setText("绘制中......")
        for i in range(3,30,3):
            Rm = self.Rms[:i, :]  # 截取前i 个样本
            Rs = self.Rss[:i, :]
            mlr = MLR(Rs, Rm)  # 由选取的n 组样本进行DS 建模
            mlr.modelling()
            Rsun = self.Rss[i:i * 2, :]  # 选取子机上同样n 组未知样本进行DS 预测
            Rmun = self.Rms[i:i * 2, :]
            Rsunp = np.dot(Rsun, mlr.A)  # A 为得到的转换矩阵，Rsunp 为预测结果
            sep.append(p.computeSEP(Rmun, Rsunp))
        x = range(3,30, 3)
        p.axes.plot(x, np.array(sep),linewidth=3, color='b',marker='o',markerfacecolor='red',markersize=12)
        p.axes.set_xlabel("样本数目（：组）")
        p.axes.set_ylabel("平均预测标准误差（SEP）")
        p.axes.set_title("样本数量 与 SEP 关系图")
        self.hlayout4.replaceWidget(self.wg, p)
        self.wg = p
        self.lb4.setText("绘制完成")
        pass



