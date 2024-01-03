__title__ = "Room Plan View"
__doc__ = "Creates room plans"

from pyrevit import revit, DB, script, forms
from Autodesk.Revit.DB import FilteredElementCollector, ViewPlan, ViewFamilyType, Transaction, BuiltInParameter, CurveLoop

doc = __revit__.ActiveUIDocument.Document
output = script.get_output()
logger = script.get_logger()

# Function to find crop box and set crop region
def set_crop_box(view, room, offset):
    # Get room bounding box
    bbox = room.get_BoundingBox(None)
    if not bbox:
        return

    # Create a rectangular crop region with an offset
    min_point = bbox.Min + DB.XYZ(-offset, -offset, 0)
    max_point = bbox.Max + DB.XYZ(offset, offset, 0)
    new_bbox = DB.BoundingBoxXYZ()
    new_bbox.Min = min_point
    new_bbox.Max = max_point

    # Set crop box
    view.CropBox = new_bbox
    view.CropBoxActive = True

# Collect and take the first view plan type
view_plan_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
floor_plan_type = next((vt for vt in view_plan_types if vt.ViewFamily == DB.ViewFamily.FloorPlan), None)

# User Input for Crop Offset and View Template
crop_offset = float(forms.ask_for_string(default="350", prompt="Crop Offset (mm)")) / 304.8
view_template_name = forms.ask_for_string(default="<None>", prompt="View Template for Plans")

# Collect all view templates for plans
view_templates = FilteredElementCollector(doc).OfClass(ViewPlan).WhereElementIsNotElementType().ToElements()
view_template_dict = {vt.Name: vt for vt in view_templates if vt.IsTemplate}
view_template_dict["<None>"] = None
chosen_view_template = view_template_dict.get(view_template_name, None)

# Collect all rooms in the project
all_rooms = FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
room_dict = {"{} - {}".format(r.Number, r.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()): r for r in all_rooms}

# Ask user to select rooms from the list
selected_room_labels = forms.SelectFromList.show(sorted(room_dict.keys()), "Select Rooms", multiselect=True)
if not selected_room_labels:
    script.exit()

selected_rooms = [room_dict[label] for label in selected_room_labels]

for room in selected_rooms:
    with Transaction(doc, "Create Plan") as t:
        t.Start()
        # Create Floor Plan
        if floor_plan_type:
            viewplan = ViewPlan.Create(doc, floor_plan_type.Id, room.LevelId)
            viewplan.Scale = 50  # Set view scale

            # Set Crop Box
            set_crop_box(viewplan, room, crop_offset)

            # Rename Floor Plan
            room_name = "{} - {}".format(room.Number, room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())
            viewplan.Name = "{} Plan".format(room_name)

            # Apply View Template if selected
            if chosen_view_template:
                viewplan.ViewTemplateId = chosen_view_template.Id

            logger.info("Created Plan for Room {}".format(room_name))

        t.Commit()
