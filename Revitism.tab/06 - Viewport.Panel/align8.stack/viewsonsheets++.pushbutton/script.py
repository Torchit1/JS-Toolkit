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

    logger.debug('Viewport types: {}'.format(all_viewport_types))

    return {vpt.name: vpt._rvt_type for vpt in all_viewport_types}

# Function to collect sheets and views
def collect_sheets_and_views():
    sheets_collector = FilteredElementCollector(revit.doc).OfClass(ViewSheet).ToElements()
    sheet_dict = {sheet.SheetNumber + " - " + sheet.Name: sheet for sheet in sheets_collector if not sheet.IsPlaceholder}

    views_collector = FilteredElementCollector(revit.doc).OfClass(View).ToElements()
    views_on_sheets = {vp.ViewId.IntegerValue for vp in FilteredElementCollector(revit.doc).OfClass(Viewport).ToElements()}
    view_dict = {view.Name: view for view in views_collector if view.Id.IntegerValue not in views_on_sheets and view.ViewType != ViewType.DrawingSheet and not view.IsTemplate and view.CanBePrinted}

    return sheet_dict, view_dict

# Function to find the top left point of the title block
def find_title_block_top_left(sheet, x_offset, y_offset):
    title_blocks = FilteredElementCollector(doc, sheet.Id).OfClass(FamilyInstance).ToElements()
    for tb in title_blocks:
        bbox = tb.get_BoundingBox(sheet)
        min_point = bbox.Min
        top_left_point = XYZ(min_point.X + x_offset, bbox.Max.Y - y_offset, 0)
        return top_left_point
    return XYZ(x_offset, y_offset, 0)

# Function to place views on a sheet
def place_views_on_sheet(sheet, views, x_offset, y_offset, row_count, column_count, row_spacing, column_spacing, viewport_type):
    start_point = find_title_block_top_left(sheet, x_offset, y_offset)

    with Transaction(doc, "Place Views on Sheet") as t:
        t.Start()
        for idx, view in enumerate(views):
            row = idx // column_count
            column = idx % column_count
            x_offset = column * column_spacing
            y_offset = -row * row_spacing
            new_center = XYZ(start_point.X + x_offset, start_point.Y + y_offset, 0)
            viewport = Viewport.Create(doc, sheet.Id, view.Id, new_center)
            viewport.ChangeTypeId(viewport_type.Id)
        t.Commit()

# Main execution
doc = revit.doc

sheet_dict, view_dict = collect_sheets_and_views()
viewport_type_dict = collect_viewport_types()

selected_sheet_name = forms.SelectFromList.show(sorted(sheet_dict.keys()), title="Select a Sheet", multiselect=False)
if not selected_sheet_name:
    forms.alert('No sheet selected.', exitscript=True)
selected_sheet = sheet_dict[selected_sheet_name]

selected_view_names = forms.SelectFromList.show(sorted(view_dict.keys()), title="Select Views", multiselect=True)
if not selected_view_names:
    forms.alert('No views selected.', exitscript=True)
selected_views = [view_dict[name] for name in selected_view_names]

selected_viewport_type_name = forms.SelectFromList.show(sorted(viewport_type_dict.keys()), title="Select Viewport Type", multiselect=False)
if not selected_viewport_type_name:
    forms.alert('No viewport type selected.', exitscript=True)
selected_viewport_type = viewport_type_dict[selected_viewport_type_name]

x_offset = float(forms.ask_for_string(default="10", prompt="X Offset from top-left corner (mm)", title="X Offset")) / 304.8
y_offset = float(forms.ask_for_string(default="10", prompt="Y Offset from top-left corner (mm)", title="Y Offset")) / 304.8
row_count = forms.ask_for_string(default="2", prompt="Number of rows", title="Rows")
column_count = forms.ask_for_string(default="2", prompt="Number of columns", title="Columns")
row_spacing = float(forms.ask_for_string(default="1000", prompt="Row Spacing (mm)", title="Row Spacing")) / 304.8
column_spacing = float(forms.ask_for_string(default="1000", prompt="Column Spacing (mm)", title="Column Spacing")) / 304.8

place_views_on_sheet(selected_sheet, selected_views, x_offset, y_offset, int(row_count), int(column_count), row_spacing, column_spacing, selected_viewport_type)

forms.alert('Views placed on sheet.')
