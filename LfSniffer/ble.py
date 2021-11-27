#! /usr/bin/python3

import asyncio
from bleak import BleakScanner, BleakClient

# Definition of constants
SNIFFER_FRAMETYPE_MASK = 0x03
SNIFFER_BUFFERFRAME_RXFRAME = 0x00
SNIFFER_BUFFERFRAME_EVENT = 0x01
SNIFFER_DATA_MASK = 0xFC

# Events definition
SNIFFER_EVENT_MSGLOST_NOSPACEINBUFFER = 0x00
SNIFFER_EVENT_MSGLOST_INCOMPLETERX = 0x01
SNIFFER_EVENT_MSGLOST_WUPWITHOUTDATADISCARDED = 0x10

def sniffer_rxframe_data_processing(length, data):
    if length != len(data):
        print("Error: Incomplete data frame")

    print("LfFrame: ", end="")
    for value in data:
        print(f"{value} ", end="")
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
    #print(f"[TMPDBG] type = {frame_type}, length = {frame_length_or_event}")

    if frame_type == SNIFFER_BUFFERFRAME_RXFRAME:
        sniffer_rxframe_data_processing(frame_length_or_event, data)
    elif frame_type == SNIFFER_BUFFERFRAME_EVENT:
        sniffer_event_processing(frame_length_or_event)
    else:
        print("Error: Invalid frame type")

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
        char_uuid = "00002adf-0000-1000-8000-00805f9b34fb" 
        sniffer_service = "00002ad0-0000-1000-8000-00805f9b34fb"
        
        services = await client.get_services()
        for s in services:
            if s.uuid == sniffer_service: 
                for x in s.characteristics:
                   if x.uuid == char_uuid:
                        char = x

        try:
            print("\nPress Ctrl-C to stop the sniffer execution\n")
            await client.start_notify(char, notification_handler)

            while True:
                await asyncio.sleep(5.0)

        except KeyboardInterrupt:
            print("Stop execution...")
            await client.stop_notify(char_uuid)
            pass

asyncio.run(main())
