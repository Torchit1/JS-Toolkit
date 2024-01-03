import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, Transaction,
                               IndependentTag, Reference, TagMode, TagOrientation, View, ViewType, ElementId)
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import script, revit

output = script.get_output()
doc = revit.doc
uidoc = revit.uidoc

def is_element_visible_in_view(view, element):
    # Corrected category filter
    category_id = element.Category.Id
    collector = FilteredElementCollector(doc, view.Id).OfCategoryId(category_id).WhereElementIsNotElementType()
    return any(e.Id == element.Id for e in collector)

def create_tag_for_element(doc, view, element):
    if not is_element_visible_in_view(view, element):
        print("Element ID {} is not visible in View ID {}.".format(element.Id, view.Id))
        return None
    try:
        tag = IndependentTag.Create(doc, view.Id, Reference(element), False, TagMode.TM_ADDBY_CATEGORY, TagOrientation.Horizontal, element.Location.Point)
        return tag
    except Exception as e:
        print("Failed to create tag for Element ID {} in View ID {}: {}".format(element.Id, view.Id, str(e)))
        return None

selected_element_ref = uidoc.Selection.PickObject(ObjectType.Element, "Select an element to tag in all views")
if selected_element_ref is None:
    TaskDialog.Show('Info', 'No element selected.')
    raise SystemExit

selected_element = doc.GetElement(selected_element_ref.ElementId)

all_views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()
target_view_types = [ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]
target_views = [v for v in all_views if v.ViewType in target_view_types and not v.IsTemplate]

tagged_views_info = []
t = Transaction(doc, 'Tag Selected Element in All Views')
t.Start()

try:
    for view in target_views:
        tag = create_tag_for_element(doc, view, selected_element)
        if tag is not None:
            view_info = {
                'View Name': view.Name, 
                'View ID': output.linkify(view.Id)
            }
            tagged_views_info.append(view_info)

    t.Commit()
except Exception as e:
    print("An error occurred: {}".format(str(e)))
    t.RollBack()

# Handle case where no tags were created
if tagged_views_info:
    table_data = [[info['View Name'], info['View ID']] for info in tagged_views_info]
    columns = ['View Name', 'View ID']
    output.print_table(table_data=table_data, title="Tagged Views", columns=columns)
else:
    output.print_md("No tags were created.")
