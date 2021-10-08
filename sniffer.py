#!/usr/bin/python3

'''
Follow the next tutorial 
https://www.pythonguis.com/tutorials/pyqt-actions-toolbars-menus/
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

        button_action = QAction("Save", self)
        button_action.setStatusTip("Save information to a file")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        toolbar.addAction(button_action)

    def onMyToolBarButtonClick(self, s):
        print("click", s)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
