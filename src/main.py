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

        self.graph: pg.GraphicsLayoutWidget = pg.GraphicsLayoutWidget()

        self.eit_plot: pg.PlotItem = self.graph.addPlot(row=0, col=0)
        self.eit_plot.setLabels(title="EIT", bottom="", left="Volatage [V]")
        self.eit_plot.showGrid(x=True, y=True)

        self.signal_plot: pg.PlotItem = self.graph.addPlot(row=1, col=0)
        self.signal_plot.setLabels(title="Signal", bottom="", left="Volatage [V]")
        self.signal_plot.showGrid(x=True, y=True)

        self.button = QtWidgets.QPushButton("Start scan")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.graph)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.scan_wrapper)

    def scan_wrapper(self):
        result = do_scan()

        self.eit_plot.clear()
        self.signal_plot.clear()

        self.eit_plot.plot(result["voltage"], result["eit_clean"])
        self.signal_plot.plot(result["voltage"], result["signal_clean"])

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())