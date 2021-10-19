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
        self.sniffer_buffer = ""

    def run(self):
        pattern = 'SnifferDATA\[\d\]:'

        while True:
            serial_line = self.serial_port.readline()
            match = re.search(pattern.encode(), serial_line)

            if match != None:
                sniffer_message = serial_line[match.span()[-1]:].decode('utf-8')
                self.sniffer_buffer += sniffer_message

                # Sending sniffer data to GUI
                self.msg.emit(sniffer_message)

            # for debugging purposes
            print(serial_line.decode('utf-8'))

    def writeCommand(self, command):
        tmp = str.encode(command + "\r\n")
        self.serial_port.write(tmp)

