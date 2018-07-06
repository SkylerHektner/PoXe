from appJar import gui
from IOHandler import IOHandler, InputState
import pyautogui
import inputs
import re

# MAIN APPLICATION
class PoXe:
    def __init__(self):
        self.app = gui()
        self.bindingsDict = dict()
        self.configureBindingsDict()
        self.configureUI()
        self.ioHandler = IOHandler(self.app, self.bindingsDict)
        self.app.setStopFunction(self.closeThreads)
        self.app.go()

    def configureBindingsDict(self):
        self.bindingsDict["Bind X Button"] = "r"
        self.bindingsDict["Bind Y Button"] = "f"
        self.bindingsDict["Bind Left Button"] = "2"
        self.bindingsDict["Bind Right Button"] = "3"
        self.bindingsDict["Bind Left Trigger"] = "1"
        self.bindingsDict["Bind Right Trigger"] = "4"
        self.bindingsDict["Bind Dpad Down"] = "w"
        self.bindingsDict["Bind Dpad Up"] = "t"
        self.bindingsDict["Bind Dpad Left"] = "q"
        self.bindingsDict["Bind Dpad Right"] = "e"

    def configureUI(self):
        # NAME
        self.app.title = "PoXe"

        # START BUTTON
        self.app.addButton("START", self.startTracking, 0, 0, 2, 2)

        # CONTROLS CONFIGURATIONS
        self.app.addLabel("A_Label", "A Binding: Left Click", 2, 0)
        self.app.setLabelAlign("A_Label", "left")
        self.app.addLabel("B_Label", "B Binding: Right Click", 3, 0)
        self.app.setLabelAlign("B_Label", "left")

        self.createBindingSet("Bind X Button", "X Binding: "+ self.bindingsDict["Bind X Button"], 4, 0)
        self.createBindingSet("Bind Y Button", "Y Binding: " + self.bindingsDict["Bind Y Button"], 5, 0)
        self.createBindingSet("Bind Left Button", "LB Binding: " + self.bindingsDict["Bind Left Button"], 6, 0)
        self.createBindingSet("Bind Right Button", "RB Binding: " + self.bindingsDict["Bind Right Button"], 7, 0)
        self.createBindingSet("Bind Left Trigger", "LT Binding: " + self.bindingsDict["Bind Left Trigger"], 8, 0)
        self.createBindingSet("Bind Right Trigger", "RT Binding: " + self.bindingsDict["Bind Right Trigger"], 9, 0)
        self.createBindingSet("Bind Dpad Down", "DPad Down Binding: " + self.bindingsDict["Bind Dpad Down"], 10, 0)
        self.createBindingSet("Bind Dpad Up", "DPad Up Binding: " + self.bindingsDict["Bind Dpad Up"], 11, 0)
        self.createBindingSet("Bind Dpad Left", "DPad Left Binding: " + self.bindingsDict["Bind Dpad Left"], 12, 0)
        self.createBindingSet("Bind Dpad Right", "DPad Right Binding: " + self.bindingsDict["Bind Dpad Right"], 13, 0)

    def createBindingSet(self, label, labelText, row, column):
        self.app.addLabel(label + "L", labelText, row, column)
        self.app.setLabelAlign(label + "L", "left")
        self.app.addButton(label, self.bindNewKey, row, column + 1)
        self.app.setButtonAlign(label, "left")
    
    def startTracking(self):
        self.ioHandler.inputActive = True
        self.ioHandler.outputActive = True
    
    def closeThreads(self):
        self.ioHandler.closeThreads = True
        self.ioHandler.inputActive = False
        self.ioHandler.outputActive = False
        return True

    def bindNewKey(self, btn):
        result = self.app.stringBox("Key Binding", btn + ": Please only enter a single letter or number (0-9)")
        match = re.search("[A-Z,a-z,0-9]", result)
        try:
            self.bindingsDict[btn] = match.group()
            self.app.setLabel(btn + "L", self.replaceLastChar(self.app.getLabel(btn + "L"), match.group()))
        except:
            self.app.warningBox("Invalid Entry", "Sorry, your entry was invalid. Please enter a single letter or number(0-9)")

    def replaceLastChar(self, oldString, newLastChar):
        s = oldString[:-1]
        s += newLastChar
        return s
        

if __name__ == "__main__":
    app = PoXe()