#! /usr/bin/python3

import asyncio
import queue
import threading

from bleak import BleakScanner, BleakClient
from pynput import keyboard

# Definition of constants
SNIFFER_FRAMETYPE_MASK = 0x03
SNIFFER_BUFFERFRAME_RXFRAME = 0x00
SNIFFER_BUFFERFRAME_EVENT = 0x01
SNIFFER_DATA_MASK = 0xFC

# Events definition
SNIFFER_EVENT_MSGLOST_NOSPACEINBUFFER = 0x00
SNIFFER_EVENT_MSGLOST_INCOMPLETERX = 0x01
SNIFFER_EVENT_MSGLOST_WUPWITHOUTDATADISCARDED = 0x10

# BLE UUID's for service and characteristics
UUID_SNIFFER_SERVICE = "00002ad0-0000-1000-8000-00805f9b34fb"
UUID_CHAR_SNIFFER_DATA = "00002adf-0000-1000-8000-00805f9b34fb" 
UUID_CHAR_SNIFFER_REMOTE = "00002ae0-0000-1000-8000-00805f9b34fb" 

# Sniffer commands
START_SIM = bytearray([0x73, 0x6e, 0x69, 0x66, 0x66, 0x65, 0x72, 0x20, 0x73, 0x74, 0x61, 0x72, 0x74, 0x73, 0x69, 0x6d, 0x00])
SNIFFER_START = bytearray([0x73, 0x6e, 0x69, 0x66, 0x66, 0x65, 0x72, 0x20, 0x73, 0x74, 0x61, 0x72, 0x74, 0x00])
SNIFFER_STOP = bytearray([0x73, 0x6e, 0x69, 0x66, 0x66, 0x65, 0x72, 0x20, 0x73, 0x74, 0x6f, 0x70, 0x00])

def sniffer_rxframe_data_processing(length, data):
    if length != len(data):
        print("Error: Incomplete data frame")

    print("LfFrame: ", end="")
    for value in data:
        print(f"{hex(value)} ", end="")
    print("")

def sniffer_event_processing(event):
    if event == SNIFFER_EVENT_MSGLOST_NOSPACEINBUFFER:
        print("Event: No space in buffer.")
    elif event == SNIFFER_EVENT_MSGLOST_INCOMPLETERX:
        print("Event: Incomplete reception.")
    elif event == SNIFFER_EVENT_MSGLOST_WUPWITHOUTDATADISCARDED:
        print("Event: Wup without data is discarded.")
    else:
        print("Error: Invalid event!")

def notification_handler(sender, data):
    sniffer_metadata = data.pop(0)
    frame_type = sniffer_metadata & SNIFFER_FRAMETYPE_MASK
    frame_length_or_event = (sniffer_metadata & SNIFFER_DATA_MASK) >> 2

    if frame_type == SNIFFER_BUFFERFRAME_RXFRAME:
        sniffer_rxframe_data_processing(frame_length_or_event, data)
    elif frame_type == SNIFFER_BUFFERFRAME_EVENT:
        sniffer_event_processing(frame_length_or_event)
    else:
        print("Error: Invalid frame type")

def read_keyboard_input(input_queue):
    print("\nPress Enter to stop the sniffer execution\n")

    while True:
        input_str = input()
        input_queue.put(input_str)

def get_sniffer_mode():
    print("\nThe following sniffer modes can be performed:")
    print("\t0. sniffer start.")
    print("\t1. sniffer startsim.")
    print("\t2. exit.")
    print("Select one: ", end="")
    mode = input()
    return mode

        
async def main():
    print("Scanning ble devices")
    devices = await BleakScanner.discover()
    print("Found ", len(devices), " device(s):")

    for d in range(len(devices)):
        print(f"\t{d}.{devices[d].name}")
    print("")

    print("Select the device to connect: ", end="")
    dev = int(input())
    ble_address = devices[dev].address
    
    async with BleakClient(ble_address) as client:
        print(f"Connected to {devices[dev].name}: {client.is_connected}")
        services = await client.get_services()
        for s in services:
            if s.uuid == UUID_SNIFFER_SERVICE: 
                for x in s.characteristics:
                   if x.uuid == UUID_CHAR_SNIFFER_DATA:
                        char = x

        while True:
            mode = int(get_sniffer_mode())

            if mode == 0:
                command = SNIFFER_START
            elif mode == 1:
                command = START_SIM
            elif mode == 2:
                break
            else:
                print("Error: Invalid sniffer mode! please try again.")
                continue
            break
            
        res = await client.write_gatt_char(UUID_CHAR_SNIFFER_REMOTE, command, True)
        await client.start_notify(char, notification_handler)

        # Stopping the execution
        input_queue = queue.Queue()
        
        input_thread = threading.Thread(target=read_keyboard_input, 
                args=(input_queue,),
                daemon=True)
        input_thread.start()

        while True:
            if (input_queue.qsize() > 0):
                input_str = input_queue.get()
                
                if (input_str == ""):
                    res = await client.write_gatt_char(UUID_CHAR_SNIFFER_REMOTE, SNIFFER_STOP, True)
                    print("Stopping execution...")
                    break

            await asyncio.sleep(2.0)

        await client.stop_notify(char)

asyncio.run(main())
