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

from PyQt5.QtWidgets import QApplication
from UserInterface import MainWindow

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
