import clr
import pyrevit.forms as forms

# Import RevitAPI
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, BuiltInParameter, ElementId

# Import RevitUI
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import Selection

# Set the active Revit application and document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
active_view = doc.ActiveView

# Define options
options = ['All Walls in View', 'Specific Wall Type']

# Show dialog and get user selection
selected_option = forms.SelectFromList.show(options, title="Select Walls", multiselect=False)

if not selected_option:
    forms.alert("You must select an option. Exiting.", exitscript=True)

walls_of_selected_type = []

if selected_option == 'All Walls in View':
    walls = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    walls_of_selected_type = [wall for wall in walls if wall.GroupId == ElementId.InvalidElementId]

elif selected_option == 'Specific Wall Type':
    selected_refs = uidoc.Selection.PickObjects(Selection.ObjectType.Element, "Select Walls of the Type to Update")
    if not selected_refs:
        forms.alert("No walls selected. Exiting.", exitscript=True)
    wall_type_id = doc.GetElement(selected_refs[0].ElementId).WallType.Id
    walls = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    walls_of_selected_type = [wall for wall in walls if wall.WallType.Id == wall_type_id and wall.GroupId == ElementId.InvalidElementId]

# Start a transaction to modify Room Bounding property
with Transaction(doc, 'Update Room Bounding') as t:
    t.Start()
    for wall in walls_of_selected_type:
        # Set Room Bounding property to False
        wall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).Set(0)
    t.Commit()
