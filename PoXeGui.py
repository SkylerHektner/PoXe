from appJar import gui
from IOHandler import IOHandler, InputState
import pyautogui
import inputs
import re
from constants import CONSTANTS
import json
import threading

# MAIN APPLICATION
class PoXe:
    def __init__(self):
        self.app = gui(useTtk=True)
        self.userSettingsDict = dict()
        self.configureUserSettingsDict()
        self.configureUI()
        self.ioHandler = IOHandler(self.app, self.userSettingsDict)
        self.app.setStopFunction(self.closeThreads)
        self.app.go()

    def configureUserSettingsDict(self):
        self.userSettingsDict[CONSTANTS.ABinding] = "mouse_left"
        self.userSettingsDict[CONSTANTS.BBinding] = "mouse_right"
        self.userSettingsDict[CONSTANTS.XBinding] = "r"
        self.userSettingsDict[CONSTANTS.YBinding] = "f"
        self.userSettingsDict[CONSTANTS.LBBinding] = "2"
        self.userSettingsDict[CONSTANTS.RBBinding] = "3"
        self.userSettingsDict[CONSTANTS.LTBinding] = "1"
        self.userSettingsDict[CONSTANTS.RTBinding] = "4"
        self.userSettingsDict[CONSTANTS.DPDBinding] = "w"
        self.userSettingsDict[CONSTANTS.DPUBinding] = "t"
        self.userSettingsDict[CONSTANTS.DPLBinding] = "q"
        self.userSettingsDict[CONSTANTS.DPRBinding] = "e"
        self.userSettingsDict[CONSTANTS.LACBinding] = "tab"
        self.userSettingsDict[CONSTANTS.RACBinding] = "g"

        self.userSettingsDict[CONSTANTS.LACBindingHideout] = "g"
        self.userSettingsDict[CONSTANTS.RACBindingHideout] = "c"

        self.userSettingsDict[CONSTANTS.LockedCursorRadius] = .23
        self.userSettingsDict[CONSTANTS.FreeCursorSpeed] = 1000.0
        self.userSettingsDict[CONSTANTS.FreeCursorAccel] = 3
        self.userSettingsDict[CONSTANTS.FrameRate] = 60
        self.userSettingsDict[CONSTANTS.InventorySnapX] = 1295
        self.userSettingsDict[CONSTANTS.InventorySnapY] = 615
        self.userSettingsDict[CONSTANTS.StashSnapX] = 335
        self.userSettingsDict[CONSTANTS.StashSnapY] = 540
        self.userSettingsDict[CONSTANTS.IncrementStep] = 54

        try:
            self.loadDefaults()
        except:
            self.saveDefaults(None)

    def saveDefaults(self, btn):
        file = open("Resources/userPrefs.json", "w")
        file.flush()
        file.write(json.dumps(self.userSettingsDict))
        file.close()
        if (btn != None):
            self.app.infoBox("Success", "New Defaults Succesfully Saved")

    def loadDefaults(self):
        text = open("Resources/userPrefs.json").read()
        tempDict = json.loads(text)
        for key in tempDict.keys():
            self.userSettingsDict[key] = tempDict[key]
        self.saveDefaults(None)

    def configureUI(self):
        # NAME
        self.app.title = "PoXe"
        self.app.setIcon("Resources/Poxe.ico")

        # LOOK & FEEL
        self.app.setResizable(canResize=False)

        # START BUTTON
        self.app.addButton("START", self.toggleTracking, 0, 0, 2, 2)
        self.app.setButtonWidth("START", 30)

        # UNIVERSAL SETTINGS
        self.app.startLabelFrame("Universal Settings", 2, 1)
        self.app.addLabel(CONSTANTS.LockedCursorRadius + "L", "Cursor Lock Mode Radius", 2, 0)
        self.app.addScale(CONSTANTS.LockedCursorRadius, 2, 1)
        self.app.setScaleRange(CONSTANTS.LockedCursorRadius, .1, .4)
        self.app.setScale(CONSTANTS.LockedCursorRadius, self.userSettingsDict[CONSTANTS.LockedCursorRadius])
        self.app.setScaleChangeFunction(CONSTANTS.LockedCursorRadius, self.newUniversalPrefsVal)
        self.app.addLabel(CONSTANTS.FreeCursorSpeed + "L", "Cursor Free Mode Speed (pixels/sec)", 3, 0)
        self.app.addSpinBoxRange(CONSTANTS.FreeCursorSpeed, 300, 2000, 3, 1)
        self.app.setSpinBoxPos(CONSTANTS.FreeCursorSpeed, self.userSettingsDict[CONSTANTS.FreeCursorSpeed] - 300)
        self.app.setSpinBoxChangeFunction(CONSTANTS.FreeCursorSpeed, self.newUniversalPrefsVal)
        self.app.addLabel(CONSTANTS.FreeCursorAccel + "L", "Cursor Free Mode Acceleration", 4, 0)
        self.app.startFrame(CONSTANTS.FreeCursorAccel + "F", 4, 1)
        self.app.addRadioButton(CONSTANTS.FreeCursorAccel, "1", 0, 0)
        self.app.addRadioButton(CONSTANTS.FreeCursorAccel, "3", 0, 1)
        self.app.addRadioButton(CONSTANTS.FreeCursorAccel, "5", 0, 2)
        if (self.userSettingsDict[CONSTANTS.FreeCursorAccel] == 3):
            self.app.setRadioButton(CONSTANTS.FreeCursorAccel, "3")
        elif (self.userSettingsDict[CONSTANTS.FreeCursorAccel] == 5):
            self.app.setRadioButton(CONSTANTS.FreeCursorAccel, "5")
        self.app.setRadioButtonChangeFunction(CONSTANTS.FreeCursorAccel, self.newUniversalPrefsVal)
        self.app.stopFrame()
        self.app.addLabel(CONSTANTS.FrameRate + "L", "Updates Per Second", 5, 0)
        self.app.addSpinBoxRange(CONSTANTS.FrameRate, 30, 90, 5, 1)
        self.app.setSpinBoxPos(CONSTANTS.FrameRate, self.userSettingsDict[CONSTANTS.FrameRate] - 30)
        self.app.setSpinBoxChangeFunction(CONSTANTS.FrameRate, self.newUniversalPrefsVal)
        self.app.stopLabelFrame()

        # HIDEOUT MODE SETTINGS
        self.app.startLabelFrame("Hideout Mode Settings", 3, 1)
        self.createSnapSet(CONSTANTS.InventorySnapX, CONSTANTS.InventorySnapX, 0, 0)
        self.createSnapSet(CONSTANTS.InventorySnapY, CONSTANTS.InventorySnapY, 1, 0)
        self.createSnapSet(CONSTANTS.StashSnapX, CONSTANTS.StashSnapX, 2, 0)
        self.createSnapSet(CONSTANTS.StashSnapY, CONSTANTS.StashSnapY, 3, 0)
        self.createSnapSet(CONSTANTS.IncrementStep, "DPad Increment: ", 4, 0)
        self.app.addButton("Hard Reset Snap Settings", self.resetSnappingVals, 5, 0, 0)
        self.createBindingSet(CONSTANTS.LACBindingHideout, "Left Analog Click Binding: " + self.userSettingsDict[CONSTANTS.LACBindingHideout], 6, 0)
        self.createBindingSet(CONSTANTS.RACBindingHideout, "Right Analog Click Binding: " + self.userSettingsDict[CONSTANTS.RACBindingHideout], 7, 0)
        self.app.stopLabelFrame()

        # MAPPING MODE SETTINGS
        self.app.startLabelFrame("Mapping Mode Settings", 2, 0, rowspan = 2)
        self.createBindingSet(CONSTANTS.ABinding, "A Binding: " + self.userSettingsDict[CONSTANTS.ABinding], 2, 0)
        self.createBindingSet(CONSTANTS.BBinding, "B Binding: " + self.userSettingsDict[CONSTANTS.BBinding], 3, 0)
        self.createBindingSet(CONSTANTS.XBinding, "X Binding: " + self.userSettingsDict[CONSTANTS.XBinding], 4, 0)
        self.createBindingSet(CONSTANTS.YBinding, "Y Binding: " + self.userSettingsDict[CONSTANTS.YBinding], 5, 0)
        self.createBindingSet(CONSTANTS.LBBinding, "LB Binding: " + self.userSettingsDict[CONSTANTS.LBBinding], 6, 0)
        self.createBindingSet(CONSTANTS.RBBinding, "RB Binding: " + self.userSettingsDict[CONSTANTS.RBBinding], 7, 0)
        self.createBindingSet(CONSTANTS.LTBinding, "LT Binding: " + self.userSettingsDict[CONSTANTS.LTBinding], 8, 0)
        self.createBindingSet(CONSTANTS.RTBinding, "RT Binding: " + self.userSettingsDict[CONSTANTS.RTBinding], 9, 0)
        self.createBindingSet(CONSTANTS.DPDBinding, "DPad Down Binding: " + self.userSettingsDict[CONSTANTS.DPDBinding], 10, 0)
        self.createBindingSet(CONSTANTS.DPUBinding, "DPad Up Binding: " + self.userSettingsDict[CONSTANTS.DPUBinding], 11, 0)
        self.createBindingSet(CONSTANTS.DPLBinding, "DPad Left Binding: " + self.userSettingsDict[CONSTANTS.DPLBinding], 12, 0)
        self.createBindingSet(CONSTANTS.DPRBinding, "DPad Right Binding: " + self.userSettingsDict[CONSTANTS.DPRBinding], 13, 0)
        self.createBindingSet(CONSTANTS.LACBinding, "Left Analog Click Binding: " + self.userSettingsDict[CONSTANTS.LACBinding], 14, 0)
        self.createBindingSet(CONSTANTS.RACBinding, "Right Analog Click Binding: " + self.userSettingsDict[CONSTANTS.RACBinding], 15, 0)
        self.app.stopLabelFrame()

        # Extras
        self.app.addButton("Instructions", self.showInstructions, 4, 0)
        self.app.addButton("Make Settings New Default", self.saveDefaults, 4, 1)

    def createBindingSet(self, title, labelText, row, column):
        self.app.addLabel(title + "L", labelText, row, column)
        self.app.setLabelAlign(title + "L", "left")
        self.app.addButton(title, self.bindNewKey, row, column + 1)
        self.app.setButtonWidth(title, 7)
        self.app.setButton(title, "Bind")

    def createSnapSet(self, title, labelText, row, column):
        self.app.addLabel(title + "L", title + ": ", row, column)
        self.app.addSpinBoxRange(title, 0, 4000, row, column + 1)
        self.app.setSpinBoxPos(title, self.userSettingsDict[title])
        self.app.setSpinBoxChangeFunction(title, self.newHideoutPrefsVal)
    
    def toggleTracking(self, btn):
        self.ioHandler.inputActive = not self.ioHandler.inputActive
        self.ioHandler.outputActive = not self.ioHandler.outputActive
        if (self.ioHandler.inputActive):
            self.app.setButton(btn, "STOP")
        else:
            self.app.setButton(btn, "START")
    
    def closeThreads(self):
        self.ioHandler.closeThreads = True
        self.ioHandler.inputActive = False
        self.ioHandler.outputActive = False
        return True

    def showInstructions(self):
        text = open("Resources/INSTRUCTIONS.txt").read()
        self.app.infoBox("Instructions", text)

    def resetSnappingVals(self):
        self.app.setSpinBoxPos(CONSTANTS.InventorySnapX, 1295)
        self.app.setSpinBoxPos(CONSTANTS.InventorySnapY, 615)
        self.app.setSpinBoxPos(CONSTANTS.StashSnapX, 335)
        self.app.setSpinBoxPos(CONSTANTS.StashSnapY, 540)
        self.app.setSpinBoxPos(CONSTANTS.IncrementStep, 54)

    def newUniversalPrefsVal(self, sender):
        try:
            if (sender == CONSTANTS.FreeCursorAccel):
                self.userSettingsDict[CONSTANTS.FreeCursorAccel] = int(self.app.getRadioButton(CONSTANTS.FreeCursorAccel))
                self.ioHandler.noLockAccel = self.userSettingsDict[CONSTANTS.FreeCursorAccel]
            elif (sender == CONSTANTS.FreeCursorSpeed):
                val = int(self.app.getSpinBox(CONSTANTS.FreeCursorSpeed))
                self.userSettingsDict[CONSTANTS.FreeCursorSpeed] = val
                self.ioHandler.noLockSens = self.userSettingsDict[CONSTANTS.FreeCursorSpeed] / self.userSettingsDict[CONSTANTS.FrameRate]
            elif (sender == CONSTANTS.FrameRate):
                val = int(self.app.getSpinBox(CONSTANTS.FrameRate))
                self.userSettingsDict[CONSTANTS.FrameRate] = val
                self.ioHandler.sleepTime = 1/self.userSettingsDict[CONSTANTS.FrameRate]
                self.ioHandler.noLockSens = self.userSettingsDict[CONSTANTS.FreeCursorSpeed] / self.userSettingsDict[CONSTANTS.FrameRate]
            elif (sender == CONSTANTS.LockedCursorRadius):
                self.userSettingsDict[CONSTANTS.LockedCursorRadius] = float(self.app.getScale(CONSTANTS.LockedCursorRadius))
                self.ioHandler.maxRange = min(self.ioHandler.xStart, self.ioHandler.yStart) * 2 * self.userSettingsDict[CONSTANTS.LockedCursorRadius]
        except:
            return

    def newHideoutPrefsVal(self, sender):
        try:
            self.userSettingsDict[sender] = int(self.app.getSpinBox(sender))
        except:
            return

    def bindNewKey(self, btn):
        result = self.app.stringBox("Key Binding", btn + ": enter single letter or numer(0-9) \nor tab | space | shift | ctrl | middle_mouse | left_mouse | right_mouse")
        if (result == None):
            return
        try:
            result = result.lower()
            if (result in CONSTANTS.SPECIAL_BINDS):
                self.userSettingsDict[btn] = result
                self.app.setLabel(btn + "L", self.replaceBindingEnd(self.app.getLabel(btn + "L"), result))
            else:
                match = re.search("[A-Z,a-z,0-9]", result)
                self.userSettingsDict[btn] = match.group()
                self.app.setLabel(btn + "L", self.replaceBindingEnd(self.app.getLabel(btn + "L"), match.group()))
        except:
            self.app.warningBox("Invalid Entry", "Sorry, your entry was invalid.")

    def replaceBindingEnd(self, oldString, newLastChar):
        s = oldString.split(":")[0] + ": " + newLastChar
        return s