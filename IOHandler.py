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
    def __init__(self, app, userPrefsDict):
        # reference to the gui for raising warning dialogues
        self.app = app
        # reference to the userPrefsDict for triggering actions
        self.userPrefsDict = userPrefsDict

        # bools for managing thread states
        self.inputActive = False
        self.outputActive = False
        self.closeThreads = False
        # float used for timing on outputThread sleep
        self.sleepTime = 1/self.userPrefsDict[CONSTANTS.FrameRate]

        # bool for tracking shift toggle
        self.shiftOn = False

        # bool for whether or not the player is in mapping mode
        self.mapping = False

        # bools for tracking exit condition (All Four Triggers)
        self.selectClose = False
        self.startClose = False

        # numbers used in mouse positioning arithmetic
        self.xStart, self.yStart = pyautogui.size()
        self.maxRange = min(self.xStart, self.yStart) * self.userPrefsDict[CONSTANTS.LockedCursorRadius]
        self.xStart /= 2
        self.yStart /= 2
        self.yStart -= 100
        self.x = self.xStart
        self.y = self.yStart
        self.xAccel = 0
        self.yAccel = 0
        self.swapCliff = 25000
        self.noLockSens = self.userPrefsDict[CONSTANTS.FreeCursorSpeed]/self.userPrefsDict[CONSTANTS.FrameRate]
        self.noLockAccel = self.userPrefsDict[CONSTANTS.FreeCursorAccel]
        self.accelDeadZone = 5000

        # the input state used when deciding how to increment the cursor
        self.inputState = InputState.LOCKED

        # a dictionary mapping input identifer strings to their respective functions
        self.funcMap = dict()
        self.populateInputFunctionMap()

        # the threads responsible for handling input/output
        self.inputThread = threading.Thread(target = self.inputLoop)
        self.inputThread.daemon = True
        self.outputThread = threading.Thread(target = self.outputLoop)
        self.outputThread.daemon = True
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
                    self.app.setButton("START", "START")
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
                            self.app.warningBox("Unsupported Key Code","Sorry, your controller may not be supported")

                    # EXIT CONDITION    
                    if (self.startClose and self.selectClose):
                        self.inputActive = False
                        self.outputActive = False
                        self.startClose, self.selectClose = False, False
                        self.app.setButton("START", "START")
            
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
        self.keyUps()

    
    def keyUps(self):
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.XBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.YBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.LBBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.RBBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.LTBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.DPDBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.DPUBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.DPLBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.DPRBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.LACBinding])
        pyautogui.keyUp(self.userPrefsDict[CONSTANTS.RACBinding])
        pyautogui.keyUp("left")
        pyautogui.keyUp("right")


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
            if (abs(e.state) < self.accelDeadZone):
                self.yAccel = 0
            else:
                self.yAccel = math.pow((e.state/32000.0),self.noLockAccel)* self.noLockSens
    def rightAnalogX(self, e):
        if (abs(e.state) > self.swapCliff):
            self.inputState = InputState.FREE 
        if (self.inputState == InputState.FREE):
            if (abs(e.state) < self.accelDeadZone):
                self.xAccel = 0
            else:
                self.xAccel = math.pow((e.state/32000.0),self.noLockAccel) * self.noLockSens
    def leftAnalogClick(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.LACBindingHideout])
    def leftAnalogClickMapping(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.LACBinding])
    def rightAnalogClick(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.RACBindingHideout])
    def rightAnalogClickMapping(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.RACBinding])

    # D PAD
    def dPadY(self, e):
        self.inputState = InputState.INCREMENT
        if (self.inputState == InputState.INCREMENT):
            self.y += self.userPrefsDict[CONSTANTS.IncrementStep] * e.state
    def dPadYMapping(self, e):
        if (e.state == 0):
            self.smartPress(False, self.userPrefsDict[CONSTANTS.DPUBinding])
            self.smartPress(False, self.userPrefsDict[CONSTANTS.DPDBinding])
        elif (e.state == -1):
            self.smartPress(True, self.userPrefsDict[CONSTANTS.DPUBinding])
        else:
            self.smartPress(True, self.userPrefsDict[CONSTANTS.DPDBinding])
    def dPadX(self, e):
        self.inputState = InputState.INCREMENT
        if (self.inputState == InputState.INCREMENT):
            self.x += self.userPrefsDict[CONSTANTS.IncrementStep] * e.state
    def dPadXMapping(self, e):
        if (e.state == 0):
            self.smartPress(False, self.userPrefsDict[CONSTANTS.DPLBinding])
            self.smartPress(False, self.userPrefsDict[CONSTANTS.DPRBinding])
        elif (e.state == -1):
            self.smartPress(True, self.userPrefsDict[CONSTANTS.DPLBinding])
        else:
            self.smartPress(True, self.userPrefsDict[CONSTANTS.DPRBinding])
    
    # TRIGGERS
    def triggerOneLeft(self, e):
        self.smartPress(bool(e.state), "left")
    def triggerOneLeftMapping(self, e):
        self.smartPress(bool(e), self.userPrefsDict[CONSTANTS.LBBinding])
    def triggerTwoLeft(self, e):
        if (e.state == 255):
            self.inputState = InputState.FREE
            self.x = self.userPrefsDict[CONSTANTS.StashSnapX]
            self.y = self.userPrefsDict[CONSTANTS.StashSnapY]
    def triggerTwoLeftMapping(self, e):
        if (e.state == 255):
            self.smartPress(True, self.userPrefsDict[CONSTANTS.LTBinding])
        else:
            self.smartPress(False, self.userPrefsDict[CONSTANTS.LTBinding])
    def triggerOneRight(self, e):
        self.smartPress(bool(e.state), "right")
    def triggerOneRightMapping(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.RBBinding])
    def triggerTwoRight(self, e):
        if (e.state == 255):
            self.inputState = InputState.FREE
            self.x = self.userPrefsDict[CONSTANTS.InventorySnapX]
            self.y = self.userPrefsDict[CONSTANTS.InventorySnapY]
    def triggerTwoRightMapping(self, e):
        if (e.state == 255):
            self.smartPress(True, self.userPrefsDict[CONSTANTS.RTBinding])
        else:
            self.smartPress(False, self.userPrefsDict[CONSTANTS.RTBinding])
        
    
    # BUTTONS
    def aButton(self, e):
        if (e.state):
            pyautogui.mouseDown()
        else:
            pyautogui.mouseUp()
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
    def aButtonMapping(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.ABinding])
    def yButton(self, e):
        if (not self.shiftOn):
            pyautogui.keyDown("shiftleft")
            self.shiftOn = True
        if (e.state):
            pyautogui.mouseDown()
        else:
            pyautogui.mouseUp()
    def yButtonMapping(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.YBinding])
    def bButton(self, e):
        if (e.state):
            pyautogui.mouseDown(button="right")
        else:
            pyautogui.mouseUp(button="right")
        if (self.shiftOn):
            pyautogui.keyUp("shiftleft")
            self.shiftOn = False
    def bButtonMapping(self, e):
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.BBinding])
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
        self.smartPress(bool(e.state), self.userPrefsDict[CONSTANTS.XBinding])

    
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

    # OUTPUT LOOP
    def outputLoop(self):
        lastX, lastY = 0, 0
        while 1:
            while self.outputActive:
                if (self.inputState == InputState.FREE):
                    self.x += self.xAccel
                    self.y -= self.yAccel
                if (self.x != lastX or self.y != lastY):
                    ctypes.windll.user32.SetCursorPos(int(self.x), int(self.y))
                    lastX, lastY = self.x, self.y
                time.sleep(self.sleepTime)

            while not self.outputActive:
                time.sleep(.5)
                if (self.closeThreads):
                    break
            if (self.closeThreads):
                break
    
    # HELPER FUNCTIONS
    def smartPress(self, down, keyCode):
        if (down):
            if (keyCode == "middle_mouse"):
                pyautogui.mouseDown(button = "middle")
            elif (keyCode == "right_mouse"):
                pyautogui.mouseDown(button = "right")
            elif (keyCode == "left_mouse"):
                pyautogui.mouseDown(button = "left")
            else:
                pyautogui.keyDown(keyCode)
        else:
            if (keyCode == "middle_mouse"):
                pyautogui.mouseUp(button = "middle")
            elif (keyCode == "right_mouse"):
                pyautogui.mouseUp(button = "right")
            elif (keyCode == "left_mouse"):
                pyautogui.mouseUp(button = "left")
            else:
                pyautogui.keyUp(keyCode)