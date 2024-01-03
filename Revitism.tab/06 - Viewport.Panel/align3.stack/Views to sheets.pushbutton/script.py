from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, View, ViewType, Viewport, Transaction, XYZ, FamilyInstance
from pyrevit import revit, DB, forms

# Get the active document
doc = revit.doc

def collect_sheets_and_views():
    # Collect sheets
    sheets_collector = FilteredElementCollector(doc).OfClass(ViewSheet).ToElements()
    sheet_dict = {sheet.SheetNumber + " - " + sheet.Name: sheet for sheet in sheets_collector if not sheet.IsPlaceholder}

    # Collect views
    views_collector = FilteredElementCollector(doc).OfClass(View).ToElements()
    views_on_sheets = {vp.ViewId.IntegerValue for vp in FilteredElementCollector(doc).OfClass(Viewport).ToElements()}
    view_dict = {view.Name: view for view in views_collector if view.Id.IntegerValue not in views_on_sheets and view.ViewType != ViewType.DrawingSheet and not view.IsTemplate and view.CanBePrinted}

    return sheet_dict, view_dict

def find_title_block_top_left(sheet, x_offset, y_offset):
    # Find the title block on the sheet
    title_blocks = FilteredElementCollector(doc, sheet.Id).OfClass(FamilyInstance).ToElements()
    for tb in title_blocks:
        # Assuming there is only one title block per sheet
        bbox = tb.get_BoundingBox(sheet)
        min_point = bbox.Min
        top_left_point = XYZ(min_point.X + x_offset, bbox.Max.Y - y_offset, 0)
        return top_left_point
    return XYZ(x_offset, y_offset, 0)  # Default top left if no title block is found

def place_views_on_sheet(sheet, views, x_offset, y_offset, row_count, column_count, row_spacing, column_spacing):
    # Find the top left of the title block to use as the starting point
    start_point = find_title_block_top_left(sheet, x_offset, y_offset)

    with Transaction(doc, "Place Views on Sheet") as t:
        t.Start()
        for idx, view in enumerate(views):
            row = idx // column_count
            column = idx % column_count
            x_offset = column * column_spacing
            y_offset = -row * row_spacing
            new_center = XYZ(start_point.X + x_offset, start_point.Y + y_offset, 0)
            Viewport.Create(doc, sheet.Id, view.Id, new_center)
        t.Commit()

sheet_dict, view_dict = collect_sheets_and_views()

# Show selection form for sheets
selected_sheet_name = forms.SelectFromList.show(sorted(sheet_dict.keys()), title="Select a Sheet", multiselect=False)
if not selected_sheet_name:
    forms.alert('No sheet selected.', exitscript=True)
selected_sheet = sheet_dict[selected_sheet_name]

# Show selection form for views
selected_view_names = forms.SelectFromList.show(sorted(view_dict.keys()), title="Select Views", multiselect=True)
if not selected_view_names:
    forms.alert('No views selected.', exitscript=True)
selected_views = [view_dict[name] for name in selected_view_names]

# Input for offset and layout parameters (metric units)
x_offset = float(forms.ask_for_string(default="75", prompt="X Offset from top-left corner (mm)", title="X Offset")) / 304.8  # Convert from mm to Revit units (feet)
y_offset = float(forms.ask_for_string(default="75", prompt="Y Offset from top-left corner (mm)", title="Y Offset")) / 304.8
row_count = forms.ask_for_string(default="2", prompt="Number of rows", title="Rows")
column_count = forms.ask_for_string(default="2", prompt="Number of columns", title="Columns")
row_spacing = float(forms.ask_for_string(default="150", prompt="Row Spacing (mm)", title="Row Spacing")) / 304.8  # Convert from mm to feet
column_spacing = float(forms.ask_for_string(default="200", prompt="Column Spacing (mm)", title="Column Spacing")) / 304.8

# Place views on the selected sheet
place_views_on_sheet(selected_sheet, selected_views, x_offset, y_offset, int(row_count), int(column_count), row_spacing, column_spacing)

forms.alert('Views placed on sheet.')