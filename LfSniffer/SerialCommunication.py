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

class SerialThread():
    def __init__(self, parent=None):
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

            # for debugging purposes
            print(serial_line.decode('utf-8'))

    def writeCommand(self, command):
        tmp = str.encode(command + "\r\n")
        self.serial_port.write(tmp)

