import inputs
import pyautogui
import ctypes
import time
import math
import threading

xStart, yStart = pyautogui.size()
xStart /= 2
yStart /= 2
yStart -= 100
global x, y
x = xStart
y = yStart
global xAdj, yAdj
xAdj = 0
yAdj = 0
maxRange = min(xStart, yStart)/2.0

global sleepTime
sleepTime = 1/60

global lockRange
lockRange = True
noLockSens = 20.0
global xAccel, yAccel
xAccel = 0.0
yAccel = 0.0
swapCliff = 25000

global closing
closing = False
leftClose = False
rightClose = False
leftCloseTrigger = False
rightCloseTrigger = False

def updatePos():
    loop = True
    sleep = globals()["sleepTime"]
    while loop:
        x = globals()['x']
        y = globals()['y']
        xAdj = globals()['xAdj']
        yAdj = globals()['yAdj']
        if not globals()['lockRange']:
            xAccel = globals()['xAccel']
            yAccel = globals()['yAccel']
            x += xAccel
            y -= yAccel
            if x > xStart * 2:
                x = xStart * 2
            elif x < 0:
                x = 0
            if y > yStart * 2:
                y = yStart * 2  
            elif y < 0:
                y = 0
            globals()['x'] = x
            globals()['y'] = y

        ctypes.windll.user32.SetCursorPos(int(x) + int(xAdj), int(y) + int(yAdj))
        time.sleep(sleep)

        loop = not globals()["closing"]

    return

thread = threading.Thread(target = updatePos)
thread.start()

while not closing:
    events = inputs.get_gamepad()
    for e in events:
        if (e.code == "SYN_REPORT"):
            pass
        elif (e.code == "ABS_X"):
            if (abs(e.state) > swapCliff):
                lockRange = True
            if (lockRange):
                x = xStart + ((e.state/32000.0) * maxRange)
        elif (e.code == "ABS_Y"):
            if (abs(e.state) > swapCliff):
                lockRange = True 
            if (lockRange):
                y = yStart - ((e.state/32000.0) * maxRange)
        elif (e.code == "ABS_RX"):
            xAccel = math.pow((e.state/32000.0),5) * noLockSens
            if (abs(e.state) > swapCliff):
                lockRange = False 
        elif (e.code == "ABS_RY"):
            yAccel = math.pow((e.state/32000.0),5)* noLockSens
            if (abs(e.state) > swapCliff):
                lockRange = False
        
        # CLOSING LOGIC
        elif (e.code == "ABS_RZ"):
            if (e.state == 255):
                rightClose = True
            else:
                rightClose = False
        elif (e.code == "ABS_Z"):
            if (e.state == 255):
                leftClose = True
            else:
                leftClose = False
        elif (e.code == "BTN_TR"):
            rightCloseTrigger = bool(e.state)
        elif (e.code == "BTN_TL"):
            leftCloseTrigger = bool(e.state)
        
        closing = leftClose and rightClose and leftCloseTrigger and rightCloseTrigger
        
    
