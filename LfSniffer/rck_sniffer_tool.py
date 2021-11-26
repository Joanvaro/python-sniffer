#! /usr/bin/python3

import argparse
import serial

from SerialCommunication import SerialThread

# parsing arguments
parser = argparse.ArgumentParser(description='RCK Sniffer tool.')
parser.add_argument('-m', '--mode', metavar='', type=str, default='serial', required=False, help='Mode to retreive data')
parser.add_argument('-p', '--port', metavar='', type=str, help='port name')
parser.add_argument('-o', '--output', metavar='', type=str, help='output name')
args = parser.parse_args()

# verifying the mode to capture data
if args.mode == 'serial':
    print('[INFO]: Starting serial communication')

    mySerial = SerialThread()

    # reading line by line 
    mySerial.run()

elif args.mode == 'ble':
    print('ble mode')
else:
    print('Error: invalid mode!')

