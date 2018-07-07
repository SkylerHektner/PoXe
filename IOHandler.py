import threading
import math
from appJar import gui
import pyautogui
import inputs
import time
import ctypes
from enum import Enum
from constants import CONSTANTS

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
        self.selectClose = False
        self.startClose = False

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
                    self.inputActive = False
                    self.outputActive = False
                    self.app.warningBox("Controller Not Found", "Sorry, no controller was found")
                    break
                
                for e in events:
                    if (e.code == "SYN_REPORT"):
                        pass
                    else:
                        try:
                            self.funcMap[e.code](e)
                        except:
                            print(e.code)
                            self.app.warningBox("Sorry, your controller may not be supported")

                    # EXIT CONDITION    
                    if (self.startClose and self.selectClose):
                        self.inputActive = False
                        self.outputActive = False
                        self.startClose, self.selectClose = False, False
            
            while not self.inputActive:
                time.sleep(.5)
                if (self.closeThreads):
                    break
            if (self.closeThreads):
                break
    
    def populateInputFunctionMap(self):
        if (not self.mapping):
            self.funcMap["ABS_X"] = self.rightAnalogX
            self.funcMap["ABS_Y"] = self.rightAnalogY
            self.funcMap["ABS_RX"] = self.leftAnalogX
            self.funcMap["ABS_RY"] = self.leftAnalogY
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
            self.funcMap["BTN_THUMBR"] = self.rightAnalogClick
            self.funcMap["BTN_THUMBL"] = self.leftAnalogClick
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
            self.funcMap["BTN_THUMBR"] = self.rightAnalogClickMapping
            self.funcMap["BTN_THUMBL"] = self.leftAnalogClickMapping

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
    def leftAnalogClick(self, e):
        pass
    def leftAnalogClickMapping(self, e):
        if (e.state):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.LACBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.LACBinding])
    def rightAnalogClick(self, e):
        pass
    def rightAnalogClickMapping(self, e):
        if (e.state):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.RACBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.RACBinding])

    # D PAD
    def dPadY(self, e):
        self.inputState = InputState.INCREMENT
        if (self.inputState == InputState.INCREMENT):
            self.y += self.step * e.state
    def dPadYMapping(self, e):
        if (e.state == 0):
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.DPUBinding])
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.DPDBinding])
        elif (e.state == -1):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.DPUBinding])
        else:
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.DPDBinding])
    def dPadX(self, e):
        self.inputState = InputState.INCREMENT
        if (self.inputState == InputState.INCREMENT):
            self.x += self.step * e.state
    def dPadXMapping(self, e):
        if (e.state == 0):
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.DPLBinding])
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.DPRBinding])
        elif (e.state == -1):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.DPLBinding])
        else:
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.DPRBinding])
    
    # TRIGGERS
    def triggerOneLeft(self, e):
        if (e.state):
            pyautogui.keyDown("left")
        else:
            pyautogui.keyUp("left")
    def triggerOneLeftMapping(self, e):
        if (e.state != 1):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.LBBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.LBBinding])
    def triggerTwoLeft(self, e):
        if (e.state == 255):
            self.inputState = InputState.FREE
            self.x = self.currencyCenterX
            self.y = self.currencyCenterY
    def triggerTwoLeftMapping(self, e):
        if (e.state == 255):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.LTBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.LTBinding])
    def triggerOneRight(self, e):
        if (e.state):
            pyautogui.keyDown("right")
        else:
            pyautogui.keyUp("right")
    def triggerOneRightMapping(self, e):
        if (e.state != 1):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.RBBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.RBBinding])
    def triggerTwoRight(self, e):
        if (e.state == 255):
            self.inputState = InputState.FREE
            self.x = self.invTopLeftX
            self.y = self.invTopLeftY
    def triggerTwoRightMapping(self, e):
        if (e.state == 255):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.RTBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.RTBinding])
        
    
    # BUTTONS
    def aButton(self, e):
        if (e.state):
            pyautogui.mouseDown()
        else:
            pyautogui.mouseUp()
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
    def yButton(self, e):
        if (not self.shiftOn):
            pyautogui.keyDown("shiftleft")
            self.shiftOn = True
        if (e.state):
            pyautogui.mouseDown()
        else:
            pyautogui.mouseUp()
    def yButtonMapping(self, e):
        if (e.state):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.YBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.YBinding])
    def bButton(self, e):
        if (e.state):
            pyautogui.mouseDown(button="right")
        else:
            pyautogui.mouseUp(button="right")
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
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
        if (e.state):
            pyautogui.keyDown(self.bindingsDict[CONSTANTS.XBinding])
        else:
            pyautogui.keyUp(self.bindingsDict[CONSTANTS.XBinding])
    
    #START/SELECT
    def startButton(self, e):
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
        if (e.state):
            self.startClose = True
            self.mapping = not self.mapping
            self.populateInputFunctionMap()
        self.startClose = bool(e.state)
    def selectButton(self, e):
        if (e.state):
            pyautogui.keyDown("escape")
        else:
            pyautogui.keyUp("escape")
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
        self.selectClose = bool(e.state)
    
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