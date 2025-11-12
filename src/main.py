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

        self.graph = pg.PlotWidget()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.graph)

        data = do_scan()
        # x = np.linspace(0, 1, len(data))
        self.graph.plotItem.plot(data)



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())