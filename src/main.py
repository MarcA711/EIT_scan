import sys
from PySide6 import QtCore, QtWidgets, QtGui, QtGraphs, QtGraphsWidgets, QtCharts
import pyqtgraph as pg
import numpy as np
from scanner import do_scan

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.graph = pg.GraphicsLayoutWidget()
        self.eit_plot = self.graph.addPlot(row=0, col=0)
        self.control_plot = self.graph.addPlot(row=1, col=0)
        self.button = QtWidgets.QPushButton("Start scan")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.graph)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.scan_wrapper)

    def scan_wrapper(self):
        data1, data2 = do_scan()
        self.eit_plot.plot(data1)
        self.control_plot.plot(data2)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())