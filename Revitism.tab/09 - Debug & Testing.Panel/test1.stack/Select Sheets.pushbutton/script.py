from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet
from pyrevit import revit, forms

# Get the active document (the open project in Revit)
doc = revit.doc

def list_sheets(doc):
    """
    List all sheets in the active Revit project, displaying the sheet number followed by the sheet name.
    """
    # Create a collector instance for collecting all sheets
    sheets_collector = FilteredElementCollector(doc).OfClass(ViewSheet)

    # List to store sheet information
    sheet_info_list = []

    # Iterate over sheets and add their numbers and names to the list
    for sheet in sheets_collector:
        # Exclude placeholder sheets
        if not sheet.IsPlaceholder:
            sheet_info = "{} - {}".format(sheet.SheetNumber, sheet.Name)
            sheet_info_list.append(sheet_info)

    # Sort the list of sheet information
    sheet_info_list.sort()

    return sheet_info_list

# Get the sorted list of sheets
sheets_list = list_sheets(doc)

# Show the selection box with multiselect disabled
selected_sheet = forms.SelectFromList.show(sheets_list, title="Select a Sheet", multiselect=False)

# Do something with the selected sheet
if selected_sheet:
    alert_message = "You selected:\n{}".format(selected_sheet)
    forms.alert(alert_message)
