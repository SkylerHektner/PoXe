from appJar import gui
from IOHandler import IOHandler, InputState
import pyautogui
import inputs
import re
from constants import CONSTANTS

# MAIN APPLICATION
class PoXe:
    def __init__(self):
        self.app = gui(useTtk=True)
        self.bindingsDict = dict()
        self.configureBindingsDict()
        self.configureUI()
        self.ioHandler = IOHandler(self.app, self.bindingsDict)
        self.app.setStopFunction(self.closeThreads)
        self.app.go()

    def configureBindingsDict(self):
        self.bindingsDict[CONSTANTS.XBinding] = "r"
        self.bindingsDict[CONSTANTS.YBinding] = "f"
        self.bindingsDict[CONSTANTS.LBBinding] = "2"
        self.bindingsDict[CONSTANTS.RBBinding] = "3"
        self.bindingsDict[CONSTANTS.LTBinding] = "1"
        self.bindingsDict[CONSTANTS.RTBinding] = "4"
        self.bindingsDict[CONSTANTS.DPDBinding] = "w"
        self.bindingsDict[CONSTANTS.DPUBinding] = "t"
        self.bindingsDict[CONSTANTS.DPLBinding] = "q"
        self.bindingsDict[CONSTANTS.DPRBinding] = "e"
        self.bindingsDict[CONSTANTS.LACBinding] = "tab"
        self.bindingsDict[CONSTANTS.RACBinding] = "g"

    def configureUI(self):
        # NAME
        self.app.title = "PoXe"
        self.app.setIcon("Poxe.ico")

        # CONFIG
        self.app.setResizable(canResize=False)
        self.app.setBg("black")
        self.app.setFg("grey")

        # START BUTTON
        self.app.addButton("START", self.startTracking, 0, 0, 2, 2)
        self.app.setButtonWidth("START", 30)

        # CONTROLS CONFIGURATIONS
        self.app.addLabel("A_Label", "A Binding: Left Click", 2, 0)
        self.app.setLabelAlign("A_Label", "left")
        self.app.addLabel("B_Label", "B Binding: Right Click", 3, 0)
        self.app.setLabelAlign("B_Label", "left")

        self.createBindingSet(CONSTANTS.XBinding, "X Binding: "+ self.bindingsDict[CONSTANTS.XBinding], 4, 0)
        self.createBindingSet(CONSTANTS.YBinding, "Y Binding: " + self.bindingsDict[CONSTANTS.YBinding], 5, 0)
        self.createBindingSet(CONSTANTS.LBBinding, "LB Binding: " + self.bindingsDict[CONSTANTS.LBBinding], 6, 0)
        self.createBindingSet(CONSTANTS.RBBinding, "RB Binding: " + self.bindingsDict[CONSTANTS.RBBinding], 7, 0)
        self.createBindingSet(CONSTANTS.LTBinding, "LT Binding: " + self.bindingsDict[CONSTANTS.LTBinding], 8, 0)
        self.createBindingSet(CONSTANTS.RTBinding, "RT Binding: " + self.bindingsDict[CONSTANTS.RTBinding], 9, 0)
        self.createBindingSet(CONSTANTS.DPDBinding, "DPad Down Binding: " + self.bindingsDict[CONSTANTS.DPDBinding], 10, 0)
        self.createBindingSet(CONSTANTS.DPUBinding, "DPad Up Binding: " + self.bindingsDict[CONSTANTS.DPUBinding], 11, 0)
        self.createBindingSet(CONSTANTS.DPLBinding, "DPad Left Binding: " + self.bindingsDict[CONSTANTS.DPLBinding], 12, 0)
        self.createBindingSet(CONSTANTS.DPRBinding, "DPad Right Binding: " + self.bindingsDict[CONSTANTS.DPRBinding], 13, 0)
        self.createBindingSet(CONSTANTS.LACBinding, "Left Analog Click Binding: " + self.bindingsDict[CONSTANTS.LACBinding], 14, 0)
        self.createBindingSet(CONSTANTS.RACBinding, "Right Analog Click Binding: " + self.bindingsDict[CONSTANTS.RACBinding], 15, 0)

    def createBindingSet(self, label, labelText, row, column):
        self.app.addLabel(label + "L", labelText, row, column)
        self.app.setLabelAlign(label + "L", "left")
        self.app.addButton(label, self.bindNewKey, row, column + 1)
        self.app.setButtonWidth(label, 20)
    
    def startTracking(self):
        self.ioHandler.inputActive = True
        self.ioHandler.outputActive = True
    
    def closeThreads(self):
        self.ioHandler.closeThreads = True
        self.ioHandler.inputActive = False
        self.ioHandler.outputActive = False
        return True

    def bindNewKey(self, btn):
        result = self.app.stringBox("Key Binding", btn + ": enter single letter, number, or tab | space | shift | middle_mouse")
        result = result.lower()
        try:
            if (result in CONSTANTS.SPECIAL_BINDS):
                self.bindingsDict[btn] = result
                self.app.setLabel(btn + "L", self.replaceBindingEnd(self.app.getLabel(btn + "L"), result))
            else:
                match = re.search("[A-Z,a-z,0-9]", result)
                self.bindingsDict[btn] = match.group()
                self.app.setLabel(btn + "L", self.replaceBindingEnd(self.app.getLabel(btn + "L"), match.group()))
        except:
            self.app.warningBox("Invalid Entry", "Sorry, your entry was invalid.")

    def replaceBindingEnd(self, oldString, newLastChar):
        s = oldString.split(":")[0] + ": " + newLastChar
        return s
        

if __name__ == "__main__":
    app = PoXe()