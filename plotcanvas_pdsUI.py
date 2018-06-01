#!/user/bin/env python3
# _*_ coding: utf-8 _*_


'PDS 算法界面的逻辑实现部分'

__author__ = "Brett"

from PyQt5.QtWidgets import *
from pdsUI import Ui_PdsDialog
import numpy as np
from plotcanvas import PlotCanvas
from PDS import PDS


class myPdsDialog(QDialog, Ui_PdsDialog):
    def __init__(self, data, parent = None):
        super(myPdsDialog, self).__init__(parent)
        self.setupUi(self)
        self.data = data
        # 全样本光谱
        self.Rms = None
        self.Rss = None
        # 部分样本光谱
        self.Rm = None
        self.Rs = None
        # 窗口大小
        self.win = 1
        # 主成分数为
        self.k = 1
        # 确定可选择窗口大小范围
        for i in range(int((700-1)/2)):
            self.cbx4.insertItem(int(i + 1), str(i + 1))

        self.n = 3  # 默认截取样本数量
        # 绑定事件
        self.cbx1.currentIndexChanged.connect(self.on_cbx1changed)
        self.cbx2.currentIndexChanged.connect(self.on_cbx2changed)
        self.cbx3.currentIndexChanged.connect(self.on_cbx3changed)
        self.cbx4.currentIndexChanged.connect(self.on_cbx4changed)
        self.cbx5.currentIndexChanged.connect(self.on_cbx5changed)
        self.cbx3.setEnabled(False)
        self.cbx4.setEnabled(False)
        self.cbx5.setEnabled(False)
        self.btn0.clicked.connect(self.plotDiff)
        self.cmpKBtn.clicked.connect(self.computeK)
        self.btn.clicked.connect(self.plotPDS)
        self.btn1.clicked.connect(self.plotSmpAndSep)
        self.btn2.clicked.connect(self.plotWinAndSep)
        self.btn3.clicked.connect(self.plotKAndSep)

    def on_cbx1changed(self):
        data = self.data
        if self.cbx1.currentIndex() == 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个master样品集!"))
            return
        matdata = data[self.cbx1.currentText()]
        self.Rms = np.array(matdata.__getitem__("data")[0][0])
        pass

    def on_cbx2changed(self):
        data = self.data
        if self.cbx2.currentIndex() == 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个slaver样品集!"))
            return
        if self.cbx1.currentIndex() == 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个master样品集!"))
            return
        if self.cbx2.currentIndex() == self.cbx1.currentIndex():
            QMessageBox.information(self, "提示",
                                    self.tr("请选择一个与主机不同的slaver样品集!"))
            return

        matdata = data[self.cbx2.currentText()]
        self.Rss = np.array(matdata.__getitem__("data")[0][0])
        self.cbx3.clear()
        self.cbx3.insertItem(0, "请选择样本数量")
        # 确定样本总数量
        for i in range(self.Rms.shape[0]):
            self.cbx3.insertItem(int(i + 1), str(i + 1))
        self.cbx3.setEnabled(True)
        self.cbx4.setEnabled(True)
        pass

    def on_cbx3changed(self):
        self.n = self.cbx3.currentIndex()
        if self.n > self.Rss.shape[0]:
            QMessageBox.information(self, "提示","样本数量过多，请重新选择")
            return
        if self.n == 1:
            QMessageBox.information(self, "提示","请选择2个以上样本")
        self.Rm = self.Rms[:self.n, :]  # 截取前n 个样本
        self.Rs = self.Rss[:self.n, :]
        self.cbx3.setEnabled(False)
        pass

# 选择完窗口大小后计算主成分数
    def on_cbx4changed(self):
        if self.cbx4.currentIndex() == 0:
            QMessageBox.information(self, "提示",
                                    self.tr("请选择窗口大小!"))
            return
        self.win = self.cbx4.currentIndex()
        self.cbx4.setEnabled(False)
        pass

    def computeK(self):
        self.cbx5.clear()
        self.cbx5.insertItem(0, "请选择主成分数")
        self.cbx5.setEnabled(False)
        QMessageBox.information(self, "提示",
                                self.tr("正在计算主成分数，请稍后...!"))
        # PDS 建模得到主成分选择范围
        pds = PDS(self.Rm, self.Rs)

        pds.model(self.win)  # 以默认值计算实际的K
        for i in range(pds.kcount):
            self.cbx5.insertItem(int(i + 1), str(i + 1))
        self.cbx5.setItemText(int(pds.k), str(pds.k) + "(推荐)")
        self.cbx5.setEnabled(True)
        QMessageBox.information(self, "提示",
                                self.tr("主成分数计算完成，请选择"))

    def on_cbx5changed(self):
        self.k = self.cbx5.currentIndex()
        self.cbx5.setEnabled(False)
        pass


    def plotDiff(self):
        p = PlotCanvas()
        x = range(1100, 2500, 2)
        offset = 0.5
        for i in range(self.n):
            y = self.Rm[i, :] + offset * i  # 源机光谱
            p.axes.plot(x, y, label='样本' + str(i + 1) + '(Master)')
            y = self.Rs[i, :] + offset * i  # 目标机光谱
            p.axes.plot(x, y, label='样本' + str(i + 1) + '(Slaver)')
        p.axes.legend()
        p.axes.set_title("两台仪器样本光谱对比(offset:" + str(offset) + ")")
        self.hlayout4.replaceWidget(self.wg, p)
        self.wg = p
        pass

    def plotPDS(self):
        pds = PDS(self.Rm, self.Rs)
        # 窗口大小选择
        pds.model(self.win, self.k)   # pds 建模 得到pds.F
        Rsun = self.Rss[:self.n, :]  # 选取子机上同样n 组未知样本进行PDS 预测
        Rsunp = pds.predict(Rsun)  # Rsunp 为预测结果
        win = self.win
        # 舍弃窗口两端
        Rmswin = self.Rms[:, win: Rsun.shape[1] - win]  #Rmswin 源机上去掉两端的光谱
        x = np.arange(1100, 2500, 2)
        xwin = x[win: Rsun.shape[1] - win]
        p = PlotCanvas()
        # 差值
        for i in range(Rsunp.shape[0]):
            y1 = p.averSpec(Rmswin) # 源机均值光谱
            p.axes.plot(xwin, y1, 'r-', label='源机均值光谱')
            y2 = Rsunp[i, :]  # 从子机预测的光谱
            p.axes.plot(xwin, y2, label='样本' + str(i + 1) + '预测值')
            # 差值
            y = y2 - y1   # 目标机光谱
            p.axes.plot(xwin, y, label='样本' + str(i + 1) + '预测偏差')
        p.axes.legend()
        p.axes.set_title("PDS算法预测结果")
        self.hlayout4.replaceWidget(self.wg, p)
        self.wg = p
        Rmun = Rmswin[:self.n, :]
        sep = p.computeSEP(Rmun, Rsunp)
        self.lb5.setVisible(True)
        self.lb5.setText('%.5f' % sep)
        pass



    def plotSmpAndSep(self):
        self.lb5.setVisible(False)
        p = PlotCanvas()
        sep = []
        QMessageBox.information(self, "tip","开始绘制请稍后...")
        for i in range(3, 30, 3):
            Rm = self.Rms[:i, :]  # 截取前i 个样本
            Rs = self.Rss[:i, :]
            pds = PDS(Rm, Rs)  # 由选取的i 组样本进行DS 建模
            win = self.win
            pds.model(win, self.k)
            Rsun = self.Rss[i:i * 2, :]  # 选取子机上同样n 组未知样本进行DS 预测
            Rmun = self.Rms[i:i * 2, :]
            Rsunp = pds.predict(Rsun)
            sep.append(p.computeSEP(Rmun[:, win: Rsun.shape[1] - win], Rsunp))
        x = range(3, 30, 3)
        p.axes.plot(x, np.array(sep), linewidth=3, color='b', marker='o', markerfacecolor='red', markersize=12)
        p.axes.set_xlabel("样本数目（：组）")
        p.axes.set_ylabel("平均预测标准误差（SEP）")
        p.axes.set_title("样本数量 与 SEP 关系图")
        self.hlayout4.replaceWidget(self.wg, p)
        self.wg = p
        self.lb4.setText("绘制完成")
        pass

    def plotWinAndSep(self):
        self.lb5.setVisible(False)
        p = PlotCanvas()
        sep = []
        QMessageBox.information(self, "tip", "开始绘制请稍后...")
        # 样本数量定为当前样本数量
        n = self.n
        Rm = self.Rms[:n, :]  # 截取前i 个样本
        Rs = self.Rss[:n, :]
        pds = PDS(Rm, Rs)  # 由选取的i 组样本进行DS 建模.
        Rsun = self.Rss[n:n * 2, :]  # 选取子机上同样n 组未知样本进行DS 预测
        Rmun = self.Rms[n:n * 2, :]
        for i in range(1, 11):
            win = i
            pds.model(win, self.k)
            Rsunp = pds.predict(Rsun)
            sep.append(p.computeSEP(Rmun[:, win: Rsun.shape[1] - win], Rsunp))
        x = range(1, 11)
        p.axes.plot(x, np.array(sep), linewidth=3, color='b', marker='o', markerfacecolor='red', markersize=12)
        p.axes.set_xlabel("窗口大小")
        p.axes.set_ylabel("平均预测标准误差（SEP）")
        p.axes.set_title("窗口大小 与 SEP 关系图")
        self.hlayout4.replaceWidget(self.wg, p)
        self.wg = p
        self.lb4.setText("绘制完成")
        pass


    def plotKAndSep(self):
        self.lb5.setVisible(False)
        p = PlotCanvas()
        sep = []
        QMessageBox.information(self, "tip", "开始绘制请稍后...")
        # 样本数量定为当前样本数量
        n = 10
        Rm = self.Rms[:n, :]  # 截取前n 个样本
        Rs = self.Rss[:n, :]
        pds = PDS(Rm, Rs)  # 由选取的i 组样本进行DS 建模
        win = self.win
        Rsun = self.Rss[n:n * 2, :]  # 选取子机上同样n 组未知样本进行PDS 预测
        Rmswin = self.Rms[:, win: Rsun.shape[1] - win]
        Rmun = Rmswin[n:n * 2, :]
        for i in range(1, n+1):
            pds.model(win, i)
            Rsunp = pds.predict(Rsun)
            sep.append(p.computeSEP(Rmun, Rsunp))
        x = range(1, n+1)
        p.axes.plot(x, np.array(sep), linewidth=3, color='b', marker='o', markerfacecolor='red', markersize=12)
        p.axes.set_xlabel("主成分个数")
        p.axes.set_ylabel("平均预测标准误差（SEP）")
        p.axes.set_title("主成分个数 与 SEP 关系图")
        self.hlayout4.replaceWidget(self.wg, p)
        self.wg = p
        self.lb4.setText("绘制完成")
        pass
