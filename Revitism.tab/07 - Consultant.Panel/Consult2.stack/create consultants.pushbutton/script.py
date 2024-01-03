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

# Read the CSV file
data_rows = []
try:
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data_rows = [row for row in reader]
except Exception as e:
    output.print_md("### Error:\nFailed to read CSV file: `{0}`".format(str(e)))
    script.exit()

# Find a Generic Model family symbol to use for creating new instances
collector = FilteredElementCollector(revit.doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_GenericModel)
generic_model_symbol = None
for elem in collector:
    generic_model_symbol = elem
    break

if not generic_model_symbol:
    output.print_md("### Error:\nNo Generic Model family symbol found.")
    script.exit()


# Transaction to create dummy elements
trans = DB.Transaction(revit.doc)
trans.Start("Create Dummy Elements for Schedule")

for row in data_rows:
    # Activate the family symbol if necessary
    if not generic_model_symbol.IsActive:
        generic_model_symbol.Activate()
        revit.doc.Regenerate()

    # Create a new Generic Model element
    new_element = revit.doc.Create.NewFamilyInstance(XYZ.Zero, generic_model_symbol, Structure.StructuralType.NonStructural)

    # Set parameters for the new element
    for param_name, param_value in row.items():
        param = new_element.LookupParameter(param_name)
        if param and not param.IsReadOnly:  # Check if the parameter is not read-only
            # Convert param_value to appropriate type if necessary
            # For now, let's assume all values are strings
            param.Set(param_value)

trans.Commit()


output.print_md("### Success:\nDummy elements created and data set.")
