import sys
from PySide6 import QtCore, QtWidgets, QtGui, QtGraphs, QtGraphsWidgets, QtCharts
from PySide6.QtCore import QThread, Signal
import pyqtgraph as pg

import pickle
from pathlib import Path

from scanner import ScanWorker

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.scan_data = { "current": None }
        self.signal_update_data = None

        self.worker_thread = QThread()
        self.scan_worker = ScanWorker()
        self.scan_worker.moveToThread(self.worker_thread)
        self.worker_thread.finished.connect(self.scan_worker.deleteLater)
        self.scan_worker.update_signal.connect(self.update_signal)
        self.scan_worker.finished_scan.connect(self.update_scan_data)
        self.worker_thread.start()

        self.model = QtGui.QStandardItemModel()
        item = self.new_item("current")
        item.setSelectable(False)
        # item.setEditable(False)
        self.model.appendRow(item)
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
        self.data_save_button = QtWidgets.QPushButton()
        self.data_button_layout.addWidget(self.data_save_button)
        self.data_save_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))
        self.data_save_button.clicked.connect(self.save_current_data)
        self.data_load_button = QtWidgets.QPushButton()
        self.data_button_layout.addWidget(self.data_load_button)
        self.data_load_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentOpen))
        self.data_load_button.clicked.connect(self.load_data)
        self.data_del_button = QtWidgets.QPushButton()
        self.data_button_layout.addWidget(self.data_del_button)
        self.data_del_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditDelete))
        self.data_del_button.clicked.connect(self.delete_data)
        self.data_list = QtWidgets.QListView()
        self.data_control_box_layout.addWidget(self.data_list)
        self.data_list.setModel(self.model)

        self.scan_control_box = QtWidgets.QGroupBox("Scan setting")
        self.properties_layout.addWidget(self.scan_control_box)
        self.scan_control_box_layout = QtWidgets.QVBoxLayout()
        self.scan_control_box.setLayout(self.scan_control_box_layout)
        self.scan_control_button_layout = QtWidgets.QHBoxLayout()
        self.scan_control_box_layout.addLayout(self.scan_control_button_layout)

        self.single_scan_button = QtWidgets.QPushButton("Single scan")
        self.scan_control_button_layout.addWidget(self.single_scan_button)
        self.single_scan_button.clicked.connect(self.scan_worker.do_single_scan)
        self.start_scanning_button = QtWidgets.QPushButton("Start scanning")
        self.scan_control_button_layout.addWidget(self.start_scanning_button)
        self.start_scanning_button.clicked.connect(self.scan_worker.do_repeated_scan)
        self.stop_scanning_button = QtWidgets.QPushButton("Stop scanning")
        self.scan_control_button_layout.addWidget(self.stop_scanning_button)
        self.stop_scanning_button.clicked.connect(self.stop_scanning)

    def new_item(self, text):
        item = QtGui.QStandardItem(text)
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        item.setCheckable(True)
        item.setEditable(False)
        item.setSelectable(True)

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

    def update_scan_data(self, result):
        self.scan_data["current"] = result
        self.signal_update_data = None
        self.plot_data()

    def update_signal(self, result):
        self.signal_update_data = result
        self.plot_data()

    def stop_scanning(self):
        self.scan_worker._stop = True

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
        if not(path.is_file()):
            return
        basename = path.stem

        with open(path, "rb") as f:
            self.scan_data[basename] = pickle.load(f)

        self.model.appendRow(self.new_item(basename))
        self.plot_data()

    def delete_data(self):
        sel_indexes = self.data_list.selectedIndexes()
        print(sel_indexes)
        for ind in sel_indexes:
            name = self.model.item(ind.row()).text()
            self.model.removeRow(ind.row())
            del self.scan_data[name]
            self.plot_data()

    def plot_data(self):
        self.eit_plot.clear()
        self.signal_plot.clear()

        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            color = pg.intColor(row)
   
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                pen = pg.mkPen(color, width=2)
                dataset_name = item.text()
                result = self.scan_data[dataset_name]

                if dataset_name == "current":
                    if self.signal_update_data is None and result is None:
                        continue
                    elif result is None:
                        self.signal_plot.plot(self.signal_update_data["voltage"], self.signal_update_data["signal_clean"], pen=pen)
                        continue
                    elif self.signal_update_data is not None and result is not None:
                        self.signal_plot.plot(self.signal_update_data["voltage"], self.signal_update_data["signal_clean"], pen=pen)
                        len_update_signal_data = len(self.signal_update_data["signal_clean"])
                        self.signal_plot.plot(result["voltage"][len_update_signal_data:], result["signal_clean"][len_update_signal_data:], pen=pen)
                        self.eit_plot.plot(result["voltage"], result["eit_clean"], pen=pen)
                        continue

                self.signal_plot.plot(result["voltage"], result["signal_clean"], pen=pen)
                self.eit_plot.plot(result["voltage"], result["eit_clean"], pen=pen)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())