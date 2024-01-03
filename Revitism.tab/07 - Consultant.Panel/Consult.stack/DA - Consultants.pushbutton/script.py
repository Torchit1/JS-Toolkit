import os
import csv
from pyrevit import revit, DB, forms
from Autodesk.Revit.DB import (Transaction, XYZ, TextNote, TextNoteType,
                               FilteredElementCollector, ViewDrafting)

# Conversion factor from millimeters to feet
mm_to_ft = 0.00328084

# Ask the user to select the CSV file
file_path = forms.pick_file(file_ext='csv')

if not file_path:
    forms.alert('No file selected.', exitscript=True)

# Read the consultants from the CSV file into a list
all_consultants = []
try:
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        all_consultants = [row for row in reader]
except Exception as e:
    forms.alert("Error reading CSV file: {0}".format(e), exitscript=True)

# Use PyRevit's form to select consultants
consultant_labels = ["{0} ({1})".format(c['Employee'], c['Company']) for c in all_consultants]
selected_labels = forms.SelectFromList.show(
    sorted(consultant_labels),
    multiselect=True,
    button_name='Select Consultants'
)

if not selected_labels:
    forms.alert('No consultants were selected.', exitscript=True)

# Filter selected consultants
selected_consultants = [c for c in all_consultants if "{0} ({1})".format(c['Employee'], c['Company']) in selected_labels]

# Start a transaction to create TextNotes
doc = revit.doc
with Transaction(doc, 'Create Consultant TextNotes') as t:
    t.Start()

    # Create or get the Drafting view named "Title Block"
    drafting_view = None
    for view in FilteredElementCollector(doc).OfClass(ViewDrafting).ToElements():
        if view.Name == "Title Block":
            drafting_view = view
            break

    if drafting_view is None:
        view_family_types = FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
        for vft in view_family_types:
            if vft.ViewFamily == DB.ViewFamily.Drafting:
                drafting_view = ViewDrafting.Create(doc, vft.Id)
                drafting_view.Name = "Title Block"
                break

    # Create TextNotes
    text_note_types = FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()
    text_note_type = text_note_types[0] if text_note_types else None

    if not text_note_type:
        forms.alert('No TextNoteType found in the document.', exitscript=True)

    # Assume column widths and row height (in feet)
    col_widths = [2, 2, 2, 2, 3]
    y_offset = 0.5  # 6 inches row height
    x, y = 0, 0  # Starting point

    col_offsets = [sum(col_widths[:i]) for i in range(len(col_widths))]

    for consultant in selected_consultants:
        for i, key in enumerate(['Discipline', 'Company', 'Employee', 'Phone', 'Email']):
            txt = consultant[key]
            point = XYZ(x + col_offsets[i], y, 0)
            TextNote.Create(doc, drafting_view.Id, point, txt, text_note_type.Id)
        y -= y_offset

    t.Commit()
