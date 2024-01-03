import sys
from pyrevit import revit, DB, forms
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, Viewport, Transaction, XYZ, ElementId, BuiltInParameter

# Function to get the ID of the 'TEMP' view template
def get_temp_view_template_id(doc):
    view_templates = FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType()
    for vt in view_templates:
        if vt.IsTemplate and vt.Name == "TEMP":
            return vt.Id
    return None

# Get the active document and the active view (which should be a sheet)
doc = revit.doc
active_view = doc.ActiveView

# Check if the active view is a sheet
if not isinstance(active_view, ViewSheet):
    forms.alert("The active view is not a sheet.", exitscript=True)

# Find the 'TEMP' view template ID
temp_view_template_id = get_temp_view_template_id(doc)
if not temp_view_template_id:
    forms.alert("No 'TEMP' view template found.", exitscript=True)
    sys.exit()

# Collect all viewports on the active sheet
viewports = FilteredElementCollector(doc, active_view.Id).OfClass(Viewport).ToElements()

# Sort viewports by the name of the views they display
sorted_viewports = sorted(viewports, key=lambda vp: doc.GetElement(vp.ViewId).Name)

# Ask user for layout parameters
row_count = int(forms.ask_for_string(default="2", prompt="Number of rows", title="Rows"))
column_count = int(forms.ask_for_string(default="2", prompt="Number of columns", title="Columns"))
top_offset = float(forms.ask_for_string(default="10", prompt="Top offset (mm)", title="Top Offset")) / 304.8
bottom_offset = float(forms.ask_for_string(default="10", prompt="Bottom offset (mm)", title="Bottom Offset")) / 304.8
left_offset = float(forms.ask_for_string(default="10", prompt="Left offset (mm)", title="Left Offset")) / 304.8
right_offset = float(forms.ask_for_string(default="10", prompt="Right offset (mm)", title="Right Offset")) / 304.8

# Calculate the total usable area based on sheet dimensions and offsets
usable_width = active_view.Outline.Max.U - active_view.Outline.Min.U - left_offset - right_offset
usable_height = active_view.Outline.Max.V - active_view.Outline.Min.V - top_offset - bottom_offset

column_spacing = usable_width / (column_count + 1)
row_spacing = usable_height / (row_count + 1)

# Apply the 'TEMP' view template to each view
original_view_templates = {}
with Transaction(doc, "Apply TEMP View Template") as t:
    t.Start()
    for vp in sorted_viewports:
        view = doc.GetElement(vp.ViewId)
        if isinstance(view, DB.View):
            # Store original view template ID
            original_view_templates[vp.Id] = view.ViewTemplateId
            # Apply 'TEMP' view template
            view.ViewTemplateId = temp_view_template_id
    t.Commit()

# Function to arrange viewports and set detail numbers
def arrange_viewports_and_set_detail_number(sorted_viewports, column_spacing, row_spacing, left_offset, top_offset):
    with Transaction(doc, "Arrange Viewports and Rename Detail Numbers") as t:
        t.Start()

        # First, rename detail numbers to a temporary unique format
        for idx, viewport in enumerate(sorted_viewports):
            temp_detail_number = "X{}".format(idx + 1)
            param = viewport.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER)
            if param:
                param.Set(temp_detail_number)

        t.Commit()

    # Assign new detail numbers in the desired order
    with Transaction(doc, "Set New Detail Numbers") as t:
        t.Start()
        detail_number = 1
        for idx, viewport in enumerate(sorted_viewports):
            # Arrange viewports
            row = idx // column_count
            column = idx % column_count
            new_x = active_view.Outline.Min.U + left_offset + (column + 1) * column_spacing
            new_y = active_view.Outline.Max.V - top_offset - (row + 1) * row_spacing
            viewport.SetBoxCenter(XYZ(new_x, new_y, 0))

            # Set the new detail number
            param = viewport.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER)
            if param:
                param.Set(str(detail_number))
                detail_number += 1

        t.Commit()

# Arrange the viewports and set detail numbers
arrange_viewports_and_set_detail_number(sorted_viewports, column_spacing, row_spacing, left_offset, top_offset)

# Revert to original view templates after placing them on the sheet
with Transaction(doc, "Revert View Templates") as t:
    t.Start()
    for vp in sorted_viewports:
        view = doc.GetElement(vp.ViewId)
        if isinstance(view, DB.View):
            # Revert to original view template
            view.ViewTemplateId = original_view_templates.get(vp.Id, ElementId.InvalidElementId)
    t.Commit()

forms.alert('Viewports arranged on the active sheet.')
