import sys
from PySide6 import QtCore, QtWidgets, QtGui, QtGraphs, QtGraphsWidgets, QtCharts
import pyqtgraph as pg

import pickle
from pathlib import Path

from scanner import do_scan

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.scan_data = {
            "current": None
        }

        self.model = QtGui.QStandardItemModel()
        self.model.appendRow(self.new_item("current"))
        self.model.itemChanged.connect(self.plot_data)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.main_split = QtWidgets.QSplitter()
        self.layout.addWidget(self.main_split)

        self.graph: pg.GraphicsLayoutWidget = pg.GraphicsLayoutWidget()
        self.main_split.addWidget(self.graph)

        self.eit_plot: pg.PlotItem = self.graph.addPlot(row=0, col=0)
        self.eit_plot.setLabels(title="EIT", bottom="", left="Volatage [V]")
        self.eit_plot.showGrid(x=True, y=True)

        self.signal_plot: pg.PlotItem = self.graph.addPlot(row=1, col=0)
        self.signal_plot.setLabels(title="Signal", bottom="", left="Volatage [V]")
        self.signal_plot.showGrid(x=True, y=True)

        self.properties = QtWidgets.QWidget()
        self.main_split.addWidget(self.properties)
        self.properties_layout = QtWidgets.QVBoxLayout()
        self.properties.setLayout(self.properties_layout)

        self.data_control_box = QtWidgets.QGroupBox("Data")
        self.properties_layout.addWidget(self.data_control_box)
        self.data_control_box_layout = QtWidgets.QVBoxLayout()
        self.data_control_box.setLayout(self.data_control_box_layout)
        self.data_button_layout = QtWidgets.QHBoxLayout()
        self.data_control_box_layout.addLayout(self.data_button_layout)
        self.data_save_button = QtWidgets.QPushButton("Save current")
        self.data_button_layout.addWidget(self.data_save_button)
        self.data_save_button.clicked.connect(self.save_current_data)
        self.data_load_button = QtWidgets.QPushButton("Load")
        self.data_button_layout.addWidget(self.data_load_button)
        self.data_load_button.clicked.connect(self.load_data)
        self.data_list = QtWidgets.QListView()
        self.data_control_box_layout.addWidget(self.data_list)
        self.data_list.setModel(self.model)

        self.scan_control_box = QtWidgets.QGroupBox("Scan setting")
        self.properties_layout.addWidget(self.scan_control_box)
        self.scan_control_box_layout = QtWidgets.QVBoxLayout()
        self.scan_control_box.setLayout(self.scan_control_box_layout)

        self.button = QtWidgets.QPushButton("Start scan")
        self.scan_control_box_layout.addWidget(self.button)
        self.button.clicked.connect(self.scan_wrapper)

    def new_item(self, text):
        item = QtGui.QStandardItem(text)
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        item.setCheckable(True)
        item.setEditable(False)

        idx = self.model.rowCount()
        color = pg.intColor(idx)
        pixmap = QtGui.QPixmap(100, 100)
        pixmap.fill(QtGui.QColor(255,255,255,255))
        painter = QtGui.QPainter(pixmap)
        painter.setBrush(color)
        painter.drawRect(0,45,100,10)
        painter.end()
        item.setIcon(pixmap)


        return item
        # self.model.appendRow(item)

    def scan_wrapper(self):
        result = do_scan()

        self.scan_data["current"] = result
        self.plot_data()

    def save_current_data(self):
        if self.scan_data["current"] is None:
            return
        path = QtWidgets.QFileDialog.getSaveFileName(filter="*.dat")
        path = Path(path[0]).with_suffix(".dat")
        
        with open(path, "wb") as f:
            pickle.dump(self.scan_data["current"], f)

        basename = path.stem
        self.scan_data[basename] = self.scan_data["current"]
        self.scan_data["current"] = None

        self.model.appendRow(self.new_item(basename))
        self.plot_data()

    def load_data(self):
        path = QtWidgets.QFileDialog.getOpenFileName(filter="*.dat")
        path = Path(path[0])
        if not(path.exists()):
            return
        basename = path.stem

        with open(path, "rb") as f:
            self.scan_data[basename] = pickle.load(f)

        self.model.appendRow(self.new_item(basename))
        self.plot_data()

    def plot_data(self):
        self.eit_plot.clear()
        self.signal_plot.clear()

        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            color = pg.intColor(row)
   
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                pen = pg.mkPen(color, width=2)
                result = self.scan_data[item.text()]
                if result is None:
                    continue
                self.eit_plot.plot(result["voltage"], result["eit_clean"], pen=pen)
                self.signal_plot.plot(result["voltage"], result["signal_clean"], pen=pen)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())