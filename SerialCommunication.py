###################################################
# 
# Class: SerialThread 
# Desciption:
# Version: 1.0
# Author: Jose Valdez
#
###################################################

import serial

from PyQt5.QtCore import pyqtSignal, QThread

class SerialThread(QThread):

    msg = pyqtSignal(str)

    def __init__(self, parent=None):
        super(SerialThread, self).__init__(parent)
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.port = '/dev/ttyUSB0'
        self.serial_port.open()

    def run(self):
        while True:
            veri = self.serial_port.readline()
            self.msg.emit(str(veri.decode('utf-8')))

    def writeCommand(self, command):
        tmp = str.encode(command + "\r\n")
        self.serial_port.write(tmp)

