#!/usr/bin/python3

'''
Follow the next tutorial 
https://www.pythonguis.com/tutorials/pyqt-actions-toolbars-menus/


For error install sudo apt-get install libxcb-xinerama0

Icons:
    The icons can be downloaded in the following link
    https://p.yusukekamiyamane.com/
'''

import sys
import matplotlib.pyplot as plt
import numpy as np

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QStatusBar

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("RCK sniffer")

        label = QLabel("Hello!")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)
        
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        start_button = QAction(QIcon("icons/arrow.png"), "Start", self)
        start_button.setStatusTip("Start sniffer execution")
        start_button.triggered.connect(self.onMyToolBarButtonClick)
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

    def onMyToolBarButtonClick(self, s):
        print("click", s)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
