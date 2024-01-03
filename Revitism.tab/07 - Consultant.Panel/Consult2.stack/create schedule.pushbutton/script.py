import clr
import csv
import os
from Autodesk.Revit.DB import *
from pyrevit import revit, DB, forms, script

output = script.get_output()

# Ask user for the folder path
folder_path = forms.pick_folder()
if not folder_path:
    script.exit()

# Construct the CSV file path
csv_file_path = os.path.join(folder_path, 'consultants.csv')

# Read the CSV file and store fieldnames
fieldnames = []
try:
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
except Exception as e:
    output.print_md("### Error:\nFailed to read CSV file: `{0}`".format(str(e)))
    script.exit()

# Start a transaction to create the schedule
trans = DB.Transaction(revit.doc)
trans.Start("Create Consultants Schedule")

# Create a new schedule for the 'Generic Models' category
schedule = ViewSchedule.CreateSchedule(revit.doc, ElementId(BuiltInCategory.OST_GenericModel))
schedule.Name = "Consultants Schedule"

# Get the ScheduleDefinition of the new schedule
sched_def = schedule.Definition

# Add shared parameters to the schedule as fields
for header in fieldnames:
    # Find the shared parameter element in the document
    shared_parameter_element = None
    for element in FilteredElementCollector(revit.doc).OfClass(SharedParameterElement):
        if element.GetDefinition().Name == header:
            shared_parameter_element = element
            break

    if shared_parameter_element:
        # Add the field to the schedule
        sched_def.AddField(ScheduleFieldType.Instance, shared_parameter_element.Id)
    else:
        output.print_md("### Warning:\nShared parameter `{0}` not found.".format(header))

# Commit the transaction to create the schedule
trans.Commit()

output.print_md("### Success:\nSchedule `{0}` has been created with the specified fields.".format(schedule.Name))
