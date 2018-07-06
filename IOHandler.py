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
    def __init__(self, app, bindingsDict):
        # reference to the gui for raising warning dialogues
        self.app = app
        # reference to the bindingsDict for triggering actions
        self.bindingsDict = bindingsDict

        # bools for managing thread states
        self.inputActive = False
        self.outputActive = False
        self.closeThreads = False

        # Inventory Snapping Positions
        self.invTopLeftX = 1295
        self.invTopLeftY = 615
        self.step = 54
        self.currencyCenterX = 335
        self.currencyCenterY = 540

        # bool for tracking shift toggle
        self.shiftOn = False

        # bool for whether or not the player is in mapping mode
        self.mapping = False

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
        if (not self.mapping):
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
            self.funcMap["BTN_START"] = self.startButton
            self.funcMap["BTN_SELECT"] = self.selectButton
        else:
            self.funcMap["ABS_X"] = self.leftAnalogX
            self.funcMap["ABS_Y"] = self.leftAnalogY
            self.funcMap["ABS_RX"] = self.rightAnalogX
            self.funcMap["ABS_RY"] = self.rightAnalogY
            self.funcMap["ABS_HAT0X"] = self.dPadXMapping
            self.funcMap["ABS_HAT0Y"] = self.dPadYMapping
            self.funcMap["ABS_Z"] = self.triggerTwoLeftMapping
            self.funcMap["ABS_RZ"] = self.triggerTwoRightMapping
            self.funcMap["BTN_TL"] = self.triggerOneLeftMapping
            self.funcMap["BTN_TR"] = self.triggerOneRightMapping
            self.funcMap["BTN_SOUTH"] = self.aButton
            self.funcMap["BTN_WEST"] = self.xButtonMapping
            self.funcMap["BTN_EAST"] = self.bButton
            self.funcMap["BTN_NORTH"] = self.yButtonMapping
            self.funcMap["BTN_START"] = self.startButton
            self.funcMap["BTN_SELECT"] = self.selectButton

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
            self.y += self.step * e.state
    def dPadYMapping(self, e):
        if (e.state == 0):
            return
        elif (e.state == -1):
            pyautogui.press(self.bindingsDict["Bind Dpad Up"])
        else:
            pyautogui.press(self.bindingsDict["Bind Dpad Down"])
    def dPadX(self, e):
        self.inputState = InputState.INCREMENT
        if (self.inputState == InputState.INCREMENT):
            self.x += self.step * e.state
    def dPadXMapping(self, e):
        if (e.state == 0):
            return
        elif (e.state == -1):
            pyautogui.press(self.bindingsDict["Bind Dpad Left"])
        else:
            pyautogui.press(self.bindingsDict["Bind Dpad Right"])
    
    # TRIGGERS
    def triggerOneLeft(self, e):
        if (e.state):
            pyautogui.press("left")
        self.leftCloseTrigger = bool(e.state)
    def triggerOneLeftMapping(self, e):
        if (e.state != 1):
            return
        pyautogui.press(self.bindingsDict["Bind Left Button"])
    def triggerTwoLeft(self, e):
        if (e.state == 255):
            self.inputState = InputState.FREE
            self.x = self.currencyCenterX
            self.y = self.currencyCenterY
            self.leftClose = True
        else:
            self.leftClose = False
    def triggerTwoLeftMapping(self, e):
        if (e.state != 1):
            return
        pyautogui.press(self.bindingsDict["Bind Left Trigger"])
    def triggerOneRight(self, e):
        if (e.state):
            pyautogui.press("right")
        self.rightCloseTrigger = bool(e.state)
    def triggerOneRightMapping(self, e):
        if (e.state != 1):
            return
        pyautogui.press(self.bindingsDict["Bind Right Button"])
    def triggerTwoRight(self, e):
        if (e.state == 255):
            self.rightClose = True
            self.inputState = InputState.FREE
            self.x = self.invTopLeftX
            self.y = self.invTopLeftY
        else:
            self.rightClose = False
    def triggerTwoRightMapping(self, e):
        if (e.state != 1):
            return
        pyautogui.press(self.bindingsDict["Bind Right Trigger"])
    
    # BUTTONS
    def aButton(self, e):
        if (e.state == 1):
            pyautogui.mouseDown()
        elif (e.state == 0):
            pyautogui.mouseUp()
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
    def yButton(self, e):
        if (e.state != 1):
            return
        if (not self.shiftOn):
            pyautogui.keyDown("shiftleft")
            self.shiftOn = True
        pyautogui.click()
    def yButtonMapping(self, e):
        if (e.state != 1):
            return
        pyautogui.press(self.bindingsDict["Bind Y Button"])
    def bButton(self, e):
        if (e.state != 1):
            return
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
        pyautogui.rightClick()
    def xButton(self, e):
        if (e.state != 1):
            return
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
        pyautogui.keyDown("ctrlleft")
        pyautogui.click()
        pyautogui.keyUp("ctrlleft")
    def xButtonMapping(self, e):
        if (e.state != 1):
            return
        pyautogui.press(self.bindingsDict["Bind X Button"])
    
    #START/SELECT
    def startButton(self, e):
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
        if (e.state):
            self.mapping = not self.mapping
            self.populateInputFunctionMap()
    def selectButton(self, e):
        if (e.state):
            pyautogui.press("escape")
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
    
    def outputLoop(self):
        lastX, lastY = 0, 0
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