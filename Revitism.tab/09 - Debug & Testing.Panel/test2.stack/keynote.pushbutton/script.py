import clr
import subprocess
import os
import time

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import ElementId
from Autodesk.Revit.UI import TaskDialog
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

signal_file_path = r"C:\Users\jesse\Documents\MyExtensions\MyFirstExtension.extension\Revitism.tab\09 - Debug & Testing.Panel\test2.stack\keynote.pushbutton\signal_file.txt"
batch_file_path = r"C:\Users\jesse\Documents\MyExtensions\MyFirstExtension.extension\Revitism.tab\09 - Debug & Testing.Panel\test2.stack\keynote.pushbutton\batch_file.bat"

def center_view_on_element(uidoc, element):
    bbox = element.get_BoundingBox(None)
    if bbox:
        uidoc.ShowElements(element)
        print("Centered view on element ID: {}".format(element.Id))

def create_signal_file():
    with open(signal_file_path, "w") as file:
        file.write("ready")
    

def wait_for_clear_signal():
    print("Waiting for signal to clear...")
    while os.path.exists(signal_file_path):
        time.sleep(0.1)
    

def process_selected_elements(doc, uidoc):
    selected_element_ids = uidoc.Selection.GetElementIds()
    if not selected_element_ids:
        TaskDialog.Show('Info', 'No elements selected.')
        return

    for element_id in selected_element_ids:
        element = doc.GetElement(element_id)
        center_view_on_element(uidoc, element)
        create_signal_file()
        call_mouse_control_batch()
        wait_for_clear_signal()

def call_mouse_control_batch():
    
    subprocess.Popen([batch_file_path], shell=True)

process_selected_elements(doc, uidoc)
