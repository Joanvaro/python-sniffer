#!/usr/bin/python3

'''
Follow the next tutorial 
https://www.pythonguis.com/tutorials/pyqt-actions-toolbars-menus/


For error install sudo apt-get install libxcb-xinerama0

Icons:
    The icons can be downloaded in the following link
    https://p.yusukekamiyamane.com/

Libraries:
    * PyQt5
    * Matplotlib
    * PySerial
'''

import sys
import serial

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QWidget

from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# For serial output
from PyQt5.QtCore import pyqtSignal, QThread

class serialThread(QThread):

    msg = pyqtSignal(str)

    def __init__(self, parent=None):
        super(serialThread, self).__init__(parent)
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.port = '/dev/ttyUSB0'
        self.serial_port.open()

    def run(self):
        while True:
            veri = self.serial_port.readline()
            self.msg.emit(str(veri))
            print(veri)

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("RCK sniffer")

        widget = QWidget()
        layout = QVBoxLayout()

        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        start_button = QAction(QIcon("icons/arrow.png"), "Start", self)
        start_button.setStatusTip("Start sniffer execution")
        start_button.triggered.connect(self.startExcecution)
        toolbar.addAction(start_button)

        toolbar.addSeparator()

        stop_button = QAction(QIcon("icons/cross.png"), "Start", self)
        stop_button.setStatusTip("Stop sniffer execution")
        stop_button.triggered.connect(self.onMyToolBarButtonClick)
        toolbar.addAction(stop_button)

        toolbar.addSeparator()

        save_button = QAction(QIcon("icons/disk.png"), "Save", self)
        save_button.setStatusTip("Save information to a file")
        save_button.triggered.connect(self.onMyToolBarButtonClick)
        toolbar.addAction(save_button)

        # Canvas matplot
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40]) # TODO make appear when execution starts
        layout.addWidget(sc)

        # Text browser
        self.textBrowser = QTextBrowser()
        self.textBrowser.setStyleSheet('font-size: 15px;')
        layout.addWidget(self.textBrowser)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def onMyToolBarButtonClick(self, s):
        print("click", s)

    def startExcecution(self):
        self.textBrowser.moveCursor(QTextCursor.Start)
        self.textBrowser.append("Starting ...")

        self.my_serial = serialThread()
        self.my_serial.msg.connect(self.textBrowser.append)
        self.my_serial.start()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
