import sys

from PyQt5.QtWidgets import QApplication, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_xlabel("波长 (nm)")
        self.axes.set_ylabel("吸光度 (AU)")
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # 计算平均光谱
    def averSpec(self, R):
        # 若只有一个样本，则平均光谱就为R
        if R.shape[0] == R.size:
            return R
        else:
            return np.mean(R, 0)

    # 计算预测标准偏差（SEP）
    def computeSEP(self, Rmun, Rsunp):
        # Rms 源机光谱，Rsunp 子机预测光谱:
        sep = 0
        for i in range(Rsunp.shape[0]):
            sep += np.sqrt((Rmun[i] - (Rsunp[i]) ** 2).sum() / (Rsunp[i].shape[0] - 1))
        # n 个 样本的平均预测标准误差
        sep = sep / Rsunp.shape[0]
        return sep
        pass