from appJar import gui

def testFunc():
    print("TEST")

app = gui()

app.addLabel("title", "Welcome to test app")

app.addButton("test", testFunc)

app.go()