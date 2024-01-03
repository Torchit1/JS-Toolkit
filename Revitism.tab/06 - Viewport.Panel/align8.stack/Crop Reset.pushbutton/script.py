__title__ = "Adjust Crop Box for Active View and Selected Room"
__doc__ = "Adjusts the crop box for the active view based on the selected room's boundaries."

from pyrevit import revit, DB, script, forms
from Autodesk.Revit.DB import FilteredElementCollector, ViewPlan, ViewFamilyType, Transaction, BuiltInParameter, CurveLoop

doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView
output = script.get_output()
logger = script.get_logger()

def set_crop_box(view, room, offset):
    bbox = room.get_BoundingBox(None)
    if not bbox:
        return

    min_point = bbox.Min + DB.XYZ(-offset, -offset, 0)
    max_point = bbox.Max + DB.XYZ(offset, offset, 0)
    new_bbox = DB.BoundingBoxXYZ()
    new_bbox.Min = min_point
    new_bbox.Max = max_point

    view.CropBox = new_bbox
    view.CropBoxActive = True

# Ensure the active view is a plan view
if not isinstance(active_view, DB.ViewPlan):
    forms.alert("The active view is not a plan view.", exitscript=True)

# Collect all rooms
rooms = FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
room_dict = {"{} - {}".format(r.Number, r.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()): r for r in rooms}

# User selects a room
selected_room_label = forms.SelectFromList.show(sorted(room_dict.keys()), "Select a Room", multiselect=False)
if not selected_room_label:
    script.exit()

selected_room = room_dict[selected_room_label]

# User Input for Crop Offset
crop_offset = float(forms.ask_for_string(default="350", prompt="Crop Offset (mm)")) / 304.8

# Apply the crop box to the active view based on the selected room
with revit.Transaction("Adjust Crop Box"):
    set_crop_box(active_view, selected_room, crop_offset)
    logger.info("Adjusted crop box for the active view based on room: {}".format(selected_room_label))
