import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, Transaction,
                               IndependentTag, Reference, TagMode, TagOrientation, View, ViewType, XYZ)
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter
from pyrevit import script, revit
from collections import defaultdict

output = script.get_output()
doc = revit.doc
uidoc = revit.uidoc

class MultipleElementsFilter(ISelectionFilter):
    def AllowElement(self, elem):
        return True

def is_element_visible_in_view(view, element):
    category_id = element.Category.Id
    collector = FilteredElementCollector(doc, view.Id).OfCategoryId(category_id).WhereElementIsNotElementType()
    return any(e.Id == element.Id for e in collector)

def get_projected_center_point(element, view):
    bbox = element.get_BoundingBox(None)
    if not bbox:
        return None

    # Calculate the center point of the bounding box
    center = bbox.Min + 0.5 * (bbox.Max - bbox.Min)

    output.print_md("Element ID: {0} | View: {1} | ViewType: {2} | Center Point: X={3}, Y={4}, Z={5}".format(
        element.Id, view.Name, view.ViewType, center.X, center.Y, center.Z))
    return center

def create_tag_for_element(doc, view, element):
    if not is_element_visible_in_view(view, element):
        return None
    center_point = get_projected_center_point(element, view)
    if center_point is None:
        return None
    try:
        return IndependentTag.Create(doc, view.Id, Reference(element), False, TagMode.TM_ADDBY_CATEGORY, TagOrientation.Horizontal, center_point)
    except Exception as e:
        return None

selection_filter = MultipleElementsFilter()
selected_element_refs = uidoc.Selection.PickObjects(ObjectType.Element, selection_filter, "Select elements to tag in all views")
if not selected_element_refs:
    TaskDialog.Show('Info', 'No elements selected.')
    raise SystemExit

selected_elements = [doc.GetElement(elem_ref.ElementId) for elem_ref in selected_element_refs]

all_views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()
target_view_types = [ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]
target_views = [v for v in all_views if v.ViewType in target_view_types and not v.IsTemplate]

tagged_views_info = defaultdict(list)
t = Transaction(doc, 'Tag Selected Elements in All Views')
t.Start()

try:
    for element in selected_elements:
        for view in target_views:
            tag = create_tag_for_element(doc, view, element)
            if tag is not None:
                tagged_views_info[view.Id].append(str(element.Id))

    t.Commit()
except Exception as e:
    print("An error occurred: " + str(e))
    t.RollBack()

table_data = []
for view_id, element_ids in tagged_views_info.items():
    view_name = doc.GetElement(view_id).Name
    elements_combined = ', '.join(element_ids)
    table_data.append([view_name, output.linkify(view_id), elements_combined])

columns = ['View Name', 'View ID', 'Element IDs']
if table_data:
    output.print_table(table_data=table_data, title="Tagged Views", columns=columns)
else:
    output.print_md("No tags were created.")
