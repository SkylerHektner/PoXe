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
        # reference to the gui for raising warning dialogues
        self.app = app

        # bools for managing thread states
        self.inputActive = False
        self.outputActive = False
        self.closeThreads = False
        

        # bools for tracking exit condition (All Four Triggers)
        self.rightClose = False
        self.leftClose = False
        self.rightCloseTrigger = False
        self.leftCloseTrigger = False

        # numbers used in mouse positioning arithmetic
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
        self.swapCliff = 25000
        self.noLockSens = 20.0

        # the input state used when deciding how to increment the cursor
        self.inputState = InputState.LOCKED

        # a dictionary mapping input identifer strings to their respective functions
        self.funcMap = dict()
        self.populateInputFunctionMap()

        # the threads responsible for handling input/output
        self.inputThread = threading.Thread(target = self.inputLoop)
        self.outputThread = threading.Thread(target = self.outputLoop)
        self.inputThread.start()
        self.outputThread.start()
    
    def inputLoop(self):
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
                    else:
                        self.funcMap[e.code](e)

                    # EXIT CONDITION    
                    if (self.leftClose and self.rightClose and self.leftCloseTrigger and self.rightCloseTrigger):
                        self.inputActive = False
                        self.outputActive = False
                        self.leftClose, self.rightClose, self.leftCloseTrigger, self.rightCloseTrigger = False, False, False, False
                    
            
            while not self.inputActive:
                time.sleep(.5)
                if (self.closeThreads):
                    break
            if (self.closeThreads):
                break
    
    def populateInputFunctionMap(self):
        self.funcMap["ABS_X"] = self.leftAnalogX
        self.funcMap["ABS_Y"] = self.leftAnalogY
        self.funcMap["ABS_RX"] = self.rightAnalogX
        self.funcMap["ABS_RY"] = self.rightAnalogY
        self.funcMap["ABS_HAT0X"] = self.dPadX
        self.funcMap["ABS_HAT0Y"] = self.dPadY
        self.funcMap["ABS_Z"] = self.triggerTwoLeft
        self.funcMap["ABS_RZ"] = self.triggerTwoRight
        self.funcMap["BTN_TL"] = self.triggerOneLeft
        self.funcMap["BTN_TR"] = self.triggerOneRight
        self.funcMap["BTN_SOUTH"] = self.aButton
        self.funcMap["BTN_WEST"] = self.xButton
        self.funcMap["BTN_EAST"] = self.bButton
        self.funcMap["BTN_NORTH"] = self.yButton

    # JOY STICKS
    def leftAnalogY(self, e):
        if (abs(e.state) > self.swapCliff):
            self.inputState = InputState.LOCKED
        if (self.inputState == InputState.LOCKED):
            self.y = self.yStart - ((e.state/32000.0) * self.maxRange)
    def leftAnalogX(self, e):
        if (abs(e.state) > self.swapCliff):
            self.inputState = InputState.LOCKED
        if (self.inputState == InputState.LOCKED):
            self.x = self.xStart + ((e.state/32000.0) * self.maxRange)
    def rightAnalogY(self, e):
        if (abs(e.state) > self.swapCliff):
            self.inputState = InputState.FREE
        if (self.inputState == InputState.FREE):
            self.yAccel = math.pow((e.state/32000.0),3)* self.noLockSens
    def rightAnalogX(self, e):
        if (abs(e.state) > self.swapCliff):
            self.inputState = InputState.FREE 
        if (self.inputState == InputState.FREE):
            self.xAccel = math.pow((e.state/32000.0),3) * self.noLockSens

    # D PAD
    def dPadY(self, e):
        self.inputState = InputState.INCREMENT
        if (self.inputState == InputState.INCREMENT):
            self.y -= self.step * e.state
    def dPadX(self, e):
        self.inputState = InputState.INCREMENT
        if (self.inputState == InputState.INCREMENT):
            self.x += self.step * e.state
    
    # TRIGGERS
    def triggerOneLeft(self, e):
        self.leftCloseTrigger = bool(e.state)
    def triggerTwoLeft(self, e):
        if (e.state == 255):
            self.leftClose = True
        else:
            self.leftClose = False
    def triggerOneRight(self, e):
        self.rightCloseTrigger = bool(e.state)
    def triggerTwoRight(self, e):
        if (e.state == 255):
            self.rightClose = True
        else:
            self.rightClose = False
    
    # BUTTONS
    def aButton(self, e):
        pass
    def xButton(self, e):
        pass
    def bButton(self, e):
        pass
    def yButton(self, e):
        pass
    
    def outputLoop(self):
        while 1:
            while self.outputActive:
                if (self.inputState == InputState.FREE):
                    self.x += self.xAccel
                    self.y -= self.yAccel
                ctypes.windll.user32.SetCursorPos(int(self.x), int(self.y))
                time.sleep(.016)

            while not self.outputActive:
                time.sleep(.5)
                if (self.closeThreads):
                    break
            if (self.closeThreads):
                break