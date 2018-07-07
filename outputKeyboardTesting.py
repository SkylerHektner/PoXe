import pyautogui
import inputs

def main():
    while 1:
        events = inputs.get_key()
        for e in events:
            print(e.code)
        events = inputs.get_mouse()
        for e in events:
            print(e.code)

if __name__ == "__main__":
    main()