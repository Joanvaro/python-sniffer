###################################################
# 
# Class: MainWindow
# Desciption:
# Version: 1.0
# Author: Jose Valdez
#
###################################################

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton

from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt

from Plot import MplCanvas
from SerialCommunication import SerialThread 

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

        # Command Line
        self.command_line_expression = QLineEdit("command", self)
        self.command_line_expression.setGeometry(80, 80, 150, 40)
        layout.addWidget(self.command_line_expression)

        # Send Button
        send_button = QPushButton("Send", self)
        send_button.setGeometry(80, 80, 93, 28)
        send_button.clicked.connect(self.sendToSerial)
        layout.addWidget(send_button)


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

        self.my_serial = SerialThread()
        self.my_serial.msg.connect(self.textBrowser.append)
        self.my_serial.start()

    def sendToSerial(self):
        self.my_serial.writeCommand(self.command_line_expression.text())
        print(self.command_line_expression.text())


