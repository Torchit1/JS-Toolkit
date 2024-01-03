import pyautogui
import time
import os

signal_file_path = r"C:\Users\jesse\Documents\MyExtensions\MyFirstExtension.extension\Revitism.tab\09 - Debug & Testing.Panel\test2.stack\keynote.pushbutton\signal_file.txt"

try:
    

    
    while not os.path.exists(signal_file_path):
        time.sleep(0.1)

    
    time.sleep(0.1)  # Wait for a moment to allow for switching to the Revit window

    screenWidth, screenHeight = pyautogui.size()
    pyautogui.moveTo(screenWidth / 2, screenHeight / 2)
    
    pyautogui.click()

    pyautogui.write('kn', interval=0.1)

    pyautogui.click()
    

    

    os.remove(signal_file_path)
    

except Exception as e:
    print("An error occurred: " + str(e))