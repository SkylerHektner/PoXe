import threading
import math
from appJar import gui
import pyautogui
import inputs
import time
import ctypes
from enum import Enum

class InputState(Enum):
    LOCKED = 1
    FREE = 2
    INCREMENT = 3

class IOHandler:
    def __init__(self, app):
        self.app = app
        self.inputThread = threading.Thread(target = self.inputLoop)
        self.outputThread = threading.Thread(target = self.outputLoop)
        self.inputActive = False
        self.outputActive = False
        self.closeThreads = False
        self.swapCliff = 25000
        self.noLockSens = 20.0

        self.xStart, self.yStart = pyautogui.size()
        self.xStart /= 2
        self.yStart /= 2
        self.yStart -= 100
        self.maxRange = min(self.xStart, self.yStart)/2.0

        self.x = self.xStart
        self.y = self.yStart

        self.xAccel = 0
        self.yAccel = 0

        self.step = 100

        self.inputState = InputState.LOCKED

        self.inputThread.start()
        self.outputThread.start()
    
    def inputLoop(self):
        rightClose, leftClose, rightCloseTrigger, leftCloseTrigger = False, False, False, False
        while 1:
            while self.inputActive:
                try:
                    events = inputs.get_gamepad()
                except:
                    print("No Gamepad Found")
                    self.inputActive = False
                    self.outputActive = False
                    self.app.warningBox("Controller Not Found", "Sorry, no controller was found")
                    break
                
                for e in events:
                    if (e.code == "SYN_REPORT"):
                        pass
                    elif (e.code == "ABS_X"):
                        if (abs(e.state) > self.swapCliff):
                            self.inputState = InputState.LOCKED
                        if (self.inputState == InputState.LOCKED):
                            self.x = self.xStart + ((e.state/32000.0) * self.maxRange)
                    elif (e.code == "ABS_Y"):
                        if (abs(e.state) > self.swapCliff):
                            self.inputState = InputState.LOCKED
                        if (self.inputState == InputState.LOCKED):
                            self.y = self.yStart - ((e.state/32000.0) * self.maxRange)
                    elif (e.code == "ABS_RX"):
                        if (abs(e.state) > self.swapCliff):
                            self.inputState = InputState.FREE 
                        if (self.inputState == InputState.FREE):
                            self.xAccel = math.pow((e.state/32000.0),3) * self.noLockSens
                    elif (e.code == "ABS_RY"):
                        if (abs(e.state) > self.swapCliff):
                            self.inputState = InputState.FREE
                        if (self.inputState == InputState.FREE):
                            self.yAccel = math.pow((e.state/32000.0),3)* self.noLockSens
                    
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
                    else:
                        print(e.code, e.state)
                    
                if (leftClose and rightClose and leftCloseTrigger and rightCloseTrigger):
                    self.inputActive = False
                    self.outputActive = False
                    leftClose, rightClose, leftCloseTrigger, rightCloseTrigger = False, False, False, False
                    
            
            while not self.inputActive:
                time.sleep(.5)
                if (self.closeThreads):
                    break
            if (self.closeThreads):
                break

    def outputLoop(self):
        while 1:
            while self.outputActive:
                if (self.inputState == InputState.LOCKED):
                    pass
                elif (self.inputState == InputState.FREE):
                    self.x += self.xAccel
                    self.y -= self.yAccel
                elif (self.inputState == InputState.INCREMENT):
                    pass
                ctypes.windll.user32.SetCursorPos(int(self.x), int(self.y))
                time.sleep(.016)

            while not self.outputActive:
                time.sleep(.5)
                if (self.closeThreads):
                    break
            if (self.closeThreads):
                break


class PoXe:
    def __init__(self):
        self.app = gui()
        self.ioHandler = IOHandler(self.app)
        self.app.addButton("START", self.startTracking)
        self.app.setStopFunction(self.closeThreads)
        self.app.go()
    
    def startTracking(self):
        self.ioHandler.inputActive = True
        self.ioHandler.outputActive = True
    
    def closeThreads(self):
        self.ioHandler.closeThreads = True
        self.ioHandler.inputActive = False
        self.ioHandler.outputActive = False
        return True

if __name__ == "__main__":
    app = PoXe()