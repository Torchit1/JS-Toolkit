import os
import subprocess

from Autodesk.Revit.DB import (Transaction, XYZ, TextNote, TextNoteType,
                               FilteredElementCollector, BuiltInCategory,
                               ModelPathUtils, ViewType, ViewFamilyType,
                               ViewFamily, ViewDrafting)
from pyrevit import revit, DB

# Conversion factor from millimeters to feet
mm_to_ft = 0.00328084

doc = revit.doc

# Check if a Drafting view named "Title Block" already exists
drafting_view = None
for view in FilteredElementCollector(doc).OfClass(ViewDrafting).ToElements():
    if view.Name == "Title Block":
        drafting_view = view
        break

# If not, create a new Drafting view named "Title Block"
if drafting_view is None:
    view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
    for vft in view_family_types:
        if vft.ViewFamily == ViewFamily.Drafting:
            with Transaction(doc, 'Create Title Block View') as t:
                t.Start()
                drafting_view = ViewDrafting.Create(doc, vft.Id)
                drafting_view.Name = "Title Block"
                t.Commit()
            break

# Get the project folder
if doc.IsWorkshared:
    model_path = doc.GetWorksharingCentralModelPath()
    folder_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(model_path)
else:
    folder_path = doc.PathName

directory = os.path.dirname(folder_path)
file_path = os.path.join(directory, 'consultants.txt')

# If consultants.txt doesn't exist, create it with sample data and instructions
if not os.path.exists(file_path):
    with open(file_path, 'w') as file:
        file.write("Architect,ABC Architects,John Doe,123-456-7890,johndoe@abcarchitects.com\n")

# Open the consultants.txt file for the user to edit
subprocess.Popen([file_path], shell=True)

try:
    with open(file_path, 'r') as file:
        consultant_data = [line.strip().split(',') for line in file.readlines()]
except FileNotFoundError:
    print("File not found: {}".format(file_path))
    exit()

text_note_types = FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()
text_note_type = text_note_types[0] if text_note_types else None

if not text_note_type:
    print("No TextNoteType found in the document.")
    exit()

with Transaction(doc, 'Create Consultant TextNotes') as t:
    t.Start()
    x = 0
    y = 0
    
    # Reset y for consultant data
    y = 0
    
    # Create TextNote for each consultant
    for data in consultant_data:
        text = "Discipline: {}\nCompany: {}\nEmployee: {}\nPhone: {}\nEmail: {}".format(*data)
        point = XYZ(x, y, 0)
        TextNote.Create(doc, drafting_view.Id, point, text, text_note_type.Id)
        y -= 2  # Adjust the Y-coordinate for the next TextNote block
    t.Commit()
