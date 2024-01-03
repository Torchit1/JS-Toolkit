import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, Transaction,
                               IndependentTag, Reference, TagMode, TagOrientation, View, ViewType, XYZ)
from Autodesk.Revit.UI import TaskDialog
from pyrevit import script, revit, forms
from collections import defaultdict

output = script.get_output()
doc = revit.doc
uidoc = revit.uidoc

def is_element_visible_in_view(view, element):
    category_id = element.Category.Id
    collector = FilteredElementCollector(doc, view.Id).OfCategoryId(category_id).WhereElementIsNotElementType()
    return any(e.Id == element.Id for e in collector)

def get_projected_center_point(element, view):
    bbox = element.get_BoundingBox(None)
    if not bbox:
        return None
    center = bbox.Min + 0.5 * (bbox.Max - bbox.Min)
    return center

def tag_elements_in_view(doc, view, elements):
    for element in elements:
        if not is_element_visible_in_view(view, element):
            continue
        center_point = get_projected_center_point(element, view)
        if center_point is None:
            continue
        try:
            tag = IndependentTag.Create(doc, view.Id, Reference(element), False, TagMode.TM_ADDBY_CATEGORY, TagOrientation.Horizontal, center_point)
            if tag is not None:
                tagged_views_info[view.Id].append(str(element.Id))
                output.print_md("Tagged Element ID: " + str(element.Id) + " in View: " + view.Name)
        except Exception as e:
            output.print_md("Failed to create tag for Element ID: " + str(element.Id) + " in View: " + view.Name + ". Error: " + str(e))

# Function to select multiple categories
def select_categories():
    categories = doc.Settings.Categories
    category_names = sorted([cat.Name for cat in categories if cat.AllowsBoundParameters])
    selected_category_names = forms.SelectFromList.show(category_names, 
                                                        multiselect=True, 
                                                        title='Select Categories to Tag', 
                                                        button_name='Select')
    if not selected_category_names:
        TaskDialog.Show('Info', 'No categories selected.')
        raise SystemExit
    return [categories.get_Item(name) for name in selected_category_names]

selected_categories = select_categories()

# Select Elements from Multiple Categories
selected_elements = []
for category in selected_categories:
    elements_collector = FilteredElementCollector(doc).OfCategoryId(category.Id).WhereElementIsNotElementType()
    selected_elements.extend([el for el in elements_collector])

# Select Views
all_views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()
target_view_types = [ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]
available_views = [v for v in all_views if v.ViewType in target_view_types and not v.IsTemplate]
view_names = sorted([v.Name for v in available_views])
selected_views = forms.SelectFromList.show(view_names, 
                                           multiselect=True, 
                                           title='Select Views',
                                           button_name='Select')

if not selected_views:
    TaskDialog.Show('Info', 'No views selected.')
    raise SystemExit

selected_views = [v for v in available_views if v.Name in selected_views]

# Tagging Process
tagged_views_info = defaultdict(list)
t = Transaction(doc, 'Tag Selected Elements in All Views')
t.Start()

try:
    for view in selected_views:
        tag_elements_in_view(doc, view, selected_elements)
    t.Commit()
except Exception as e:
    print("An error occurred: " + str(e))
    t.RollBack()

# Display Results
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
