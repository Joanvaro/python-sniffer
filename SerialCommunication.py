###################################################
# 
# Class: SerialThread 
# Desciption:
# Version: 1.0
# Author: Jose Valdez
#
###################################################

import re
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
        pattern = 'SnifferDATA\[\d\]:'

        while True:
            veri = self.serial_port.readline()

            x =re.search(pattern.encode(), veri)

            if x != None:
                #print(veri[x.span()[-1]:].decode('utf-8'))
                self.msg.emit(str(veri[x.span()[-1]:].decode('utf-8')))

            #self.msg.emit(str(veri.decode('utf-8')))

    def writeCommand(self, command):
        tmp = str.encode(command + "\r\n")
        self.serial_port.write(tmp)

