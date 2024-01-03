import sys
from pyrevit import revit, DB, script, forms
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, View, ViewType, Viewport, Transaction, XYZ, FamilyInstance, ElementType, BuiltInCategory

# Logger
logger = script.get_logger()

# Class to encapsulate viewport type functionality
class ViewPortType:
    def __init__(self, rvt_element_type):
        self._rvt_type = rvt_element_type

    def __str__(self):
        return revit.query.get_name(self._rvt_type)

    @property
    def name(self):
        return str(self)

# Function to collect viewport types
def collect_viewport_types():
    all_element_types = DB.FilteredElementCollector(revit.doc).OfClass(DB.ElementType).ToElements()
    all_viewport_types = [ViewPortType(x) for x in all_element_types if x.FamilyName == 'Viewport']
    return {vpt.name: vpt._rvt_type for vpt in all_viewport_types}

# Get the current document
doc = revit.doc

# Get all sheets in the document
sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
sheet_dict = {"{} - {}".format(sheet.SheetNumber, sheet.Name): sheet for sheet in sheets}

# Sort the sheet names (keys of the dictionary) before showing the form
sorted_sheet_names = sorted(sheet_dict.keys())

# Show a form to the user to select sheets
selected_sheet_names = forms.SelectFromList.show(sorted_sheet_names, multiselect=True, title='Select Sheets', button_name='Select')

# Check if the user selected any sheets
if not selected_sheet_names:
    print("No sheets selected. Exiting.")
    sys.exit()

# Collect viewport types
viewport_type_dict = collect_viewport_types()
selected_viewport_type_name = forms.SelectFromList.show(sorted(viewport_type_dict.keys()), title="Select Viewport Type", button_name='Select')

if not selected_viewport_type_name:
    print("No viewport type selected. Exiting.")
    sys.exit()

selected_viewport_type = viewport_type_dict[selected_viewport_type_name].Id

# Iterate over selected sheets
for sheet_name in selected_sheet_names:
    sheet = sheet_dict[sheet_name]

    # Start a new transaction for each sheet
    with Transaction(doc, 'Re-add Viewports on {}'.format(sheet_name)) as t:
        t.Start()

        # Get all viewports on the selected sheet
        viewports_on_sheet = FilteredElementCollector(doc, sheet.Id).OfCategory(BuiltInCategory.OST_Viewports).ToElements()

        # Collect data about viewports, then delete them
        viewport_data = []
        for vp in viewports_on_sheet:
            view_id = vp.ViewId
            box_center = vp.GetBoxCenter()
            viewport_data.append((view_id, box_center))
            doc.Delete(vp.Id)

        # Re-add viewports to the sheet with the selected viewport type
        for view_id, box_center in viewport_data:
            new_vp = Viewport.Create(doc, sheet.Id, view_id, box_center)
            new_vp.ChangeTypeId(selected_viewport_type)

        # Commit the transaction
        t.Commit()
