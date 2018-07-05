from appJar import gui
from IOHandler import IOHandler, InputState

# MAIN APPLICATION
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