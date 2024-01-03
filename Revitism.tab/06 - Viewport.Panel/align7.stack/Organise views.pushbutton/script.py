import sys
from pyrevit import revit, DB, forms
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, Viewport, Transaction, XYZ

# Get the active document and the active view (which should be a sheet)
doc = revit.doc
active_view = doc.ActiveView

# Check if the active view is a sheet
if not isinstance(active_view, ViewSheet):
    forms.alert("The active view is not a sheet.", exitscript=True)

# Function to find the top left point of the title block
def find_title_block_top_left(sheet, x_offset, y_offset):
    title_blocks = FilteredElementCollector(doc, sheet.Id).OfClass(DB.FamilyInstance).ToElements()
    for tb in title_blocks:
        bbox = tb.get_BoundingBox(sheet)
        min_point = bbox.Min
        top_left_point = XYZ(min_point.X + x_offset, bbox.Max.Y - y_offset, 0)
        return top_left_point
    return XYZ(x_offset, y_offset, 0)

# Function to place views on a sheet
def arrange_views_on_sheet(sheet, x_offset, y_offset, row_count, column_count, row_spacing, column_spacing):
    start_point = find_title_block_top_left(sheet, x_offset, y_offset)
    viewports = FilteredElementCollector(doc, sheet.Id).OfClass(Viewport).ToElements()

    with Transaction(doc, "Arrange Views on Sheet") as t:
        t.Start()
        for idx, viewport in enumerate(viewports):
            row = idx // column_count
            column = idx % column_count
            new_x_offset = column * column_spacing
            new_y_offset = -row * row_spacing
            new_center = XYZ(start_point.X + new_x_offset, start_point.Y + new_y_offset, 0)
            viewport.SetBoxCenter(new_center)
        t.Commit()

# User inputs for arrangement
x_offset = float(forms.ask_for_string(default="71", prompt="X Offset from top-left corner (mm)", title="X Offset")) / 304.8
y_offset = float(forms.ask_for_string(default="71", prompt="Y Offset from top-left corner (mm)", title="Y Offset")) / 304.8
row_count = int(forms.ask_for_string(default="4", prompt="Number of rows", title="Rows"))
column_count = int(forms.ask_for_string(default="4", prompt="Number of columns", title="Columns"))
row_spacing = float(forms.ask_for_string(default="125", prompt="Row Spacing (mm)", title="Row Spacing")) / 304.8
column_spacing = float(forms.ask_for_string(default="125", prompt="Column Spacing (mm)", title="Column Spacing")) / 304.8

# Arrange views on the active sheet
arrange_views_on_sheet(active_view, x_offset, y_offset, row_count, column_count, row_spacing, column_spacing)

forms.alert('Views arranged on the active sheet.')
