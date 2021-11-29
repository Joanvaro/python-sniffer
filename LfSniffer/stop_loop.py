#! /usr/bin/python3

import time
from pynput import keyboard
count = 0
stop = 0

def press_callback(key):

    if key == keyboard.Key.enter:
        def stop_loop():
            global stop
            stop = 1
            return stop
        print('Get Out')
        stop = stop_loop()
     

    return stop
    
l = keyboard.Listener(on_press=press_callback)
l.start()

while True:
    count += 1
    print (count)
    time.sleep(1)
    if stop == 1:
        break    
