#!/user/bin/env python3
# _*_ coding: utf-8 _*_


'a test module'

__author__ = "Brett"
import sys
from PyQt5.QtWidgets import *
import scipy.io as sio
from testUI import Ui_MainWindow
from plotcanvas_dsUI import myDsDialog
from plotcanvas_pdsUI import myPdsDialog
from plotcanvas_shenksUI import mySksDialog
from  plotcanvas_compareUI import myComDialog
from PyQt5.QtCore import *
import numpy as np
from plotcanvas import PlotCanvas
import cgitb
cgitb.enable( format = 'text')     #  程序崩溃不会结束

class myMainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(myMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.cbx.insertItem(0, "选择数据集")
        self.cbx.insertItem(1, "m5spec")
        self.cbx.insertItem(2, "mp5spec")
        self.cbx.insertItem(3, "mp6spec")
        self.cbx.insertItem(4, "m5nbs")
        self.cbx.insertItem(5, "mp5nbs")
        self.cbx.insertItem(6, "mp6nbs")
        # 绑定事件
        self.btn.clicked.connect(self.on_loadBtn_clicked)
        self.btn1.clicked.connect(self.jump2ds)
        self.btn2.clicked.connect(self.jump2pds)
        self.btn3.clicked.connect(self.jump2shenks)
        self.compareBtn.clicked.connect(self.jump2comp)
        self.cbx.currentIndexChanged.connect(self.on_comboxchanged)
        self.ds = None          # 三个子窗体
        self.pds = None
        self.sks = None
        self.data = None        # 传递的数据

    @pyqtSlot()
    def on_loadBtn_clicked(self):
        """
        Slot documentation goes here.
        """
        openfile_name, filetype = QFileDialog.getOpenFileName(self, '选择需要导入的数据文件', '')
        if openfile_name != None:
            self.data = sio.loadmat(openfile_name)
            self.statusbar.showMessage("导入数据成功")
        pass

    @pyqtSlot()
    def jump2ds(self):
        self.ds = myDsDialog(self.data)
        self.ds.exec_()

    @pyqtSlot()
    def jump2pds(self):
        self.pds = myPdsDialog(self.data)
        self.pds.exec_()

    @pyqtSlot()
    def jump2shenks(self):
        self.sks = mySksDialog(self.data)
        self.sks.exec_()

    @pyqtSlot()

    def jump2comp(self):
        self.comp = myComDialog(self.data)
        self.comp.exec_()

    @pyqtSlot()
    def on_comboxchanged(self):
        """
        Slot documentation goes here.
        """
        self.statusbar.showMessage("数据加载中...")
        data = self.data
        matdata = data[self.cbx.currentText()]
        input_table = np.array(matdata.__getitem__("data")[0][0])
        input_table_rows = input_table.shape[0]
        # 获取表格行数
        input_table_colunms = input_table.shape[1]
        # 获取表格列数
        input_table_header = list(map(str, range(1100, 2500, 2)))
        # 获取表头
        # print(input_table_header)
        ###===========读取表格，转换表格，==============================
        ###===========给tablewidget设置行列表头========================
        self.tw.setColumnCount(input_table_colunms)
        # 设置表格列数
        self.tw.setRowCount(input_table_rows)
        # 设置表格行数
        self.tw.setHorizontalHeaderLabels(input_table_header)
        # 给tablewidget设置行列表头
        ###===========遍历表格每个元素，同时添加到tablewidget中===========
        for i in range(input_table_rows):
            input_table_rows_values = input_table[i]
            # print(input_table_rows_values)
            # input_table_rows_values_array = np.array(input_table_rows_values)
            # input_table_rows_values_list = input_table_rows_values_array.tolist()[0]
            # print(input_table_rows_values_list)
            for j in range(input_table_colunms):
                input_table_items_list = input_table_rows_values[j]
                # print(input_table_items_list)
                # print(type(input_table_items_list))

                ###==============将遍历的元素添加到tablewidget中并显示=======================

                input_table_items = str(input_table_items_list)
                newItem = QTableWidgetItem(input_table_items)
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tw.setItem(i, j, newItem)

        self.plot()
        self.statusbar.showMessage("数据加载完成")

    # 绘制光谱图
    def plot(self):
        p = PlotCanvas(dpi=75)
        data = self.data
        matdata = data[self.cbx.currentText()]
        arrdata = np.array(matdata.__getitem__("data")[0][0])
        x = np.arange(1100, 2500, 2)
        for i in range(arrdata.shape[0]):
            y = arrdata[i]
            p.axes.plot(x, y, 'r-')
        p.axes.set_title(self.cbx.currentText()+ "80组玉米样本光谱")
        self.hlayout3.replaceWidget(self.wg1, p)
        self.wg1 = p

        # 绘制均值光谱
        p2 = PlotCanvas(dpi=75)
        y = p2.averSpec(arrdata)
        p2.axes.plot(x, y, 'r-')
        p2.axes.set_title(self.cbx.currentText())
        self.hlayout3.replaceWidget(self.wg2, p2)
        self.wg2 = p2



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = myMainWindow()
    ui.show()
    sys.exit(app.exec_())