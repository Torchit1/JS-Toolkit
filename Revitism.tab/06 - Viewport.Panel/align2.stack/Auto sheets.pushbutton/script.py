import clr
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ViewType, ViewSheet, Viewport, XYZ
from pyrevit import revit, forms

doc = revit.doc
uidoc = revit.uidoc

# Function to add view to sheet at specific location
def add_view_to_sheet(sheet, view, location):
    try:
        viewport = Viewport.Create(revit.doc, sheet.Id, view.Id, XYZ(location, location, 0))
        return viewport
    except Exception as e:
        print("Error adding view to sheet: " + str(e))

# Collect and filter views and sheets
all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

# Get unique view types in the document
view_types = list(set([view.ViewType for view in all_views]))

# Select view types from a list
selected_view_types = forms.SelectFromList.show(view_types, button_name='Select View Types', multiselect=True)

# Filter views based on selected view types
filtered_views = [view for view in all_views if view.ViewType in selected_view_types]

# Group views by name
grouped_views = {}
for view in filtered_views:
    name = view.Name.split("-")[0].strip()
    grouped_views.setdefault(name, []).append(view)

# Select sheet from a list
sheet_dict = {sheet.Name: sheet for sheet in sheets}
selected_sheet_name = forms.SelectFromList.show(sorted(sheet_dict.keys()), button_name='Select Sheet', multiselect=False)
selected_sheet = sheet_dict[selected_sheet_name]

# Prepare a message to show to the user
message = "The following views will be added to the sheet {}:\n\n".format(selected_sheet_name)
sheet_name = selected_sheet_name.split("-")[0].strip()

if sheet_name in grouped_views:
    views_for_sheet = grouped_views[sheet_name]
    views_for_sheet = sorted(views_for_sheet, key=lambda v: (v.ViewType != ViewType.FloorPlan, v.Name))
    message += ', '.join([view.Name for view in views_for_sheet])

# Show message to user
confirm = forms.alert(message, yes=True, no=True, title='Confirm Addition of Views to Sheet')

# If user confirms, add views to sheet
if confirm:
    with revit.Transaction("Add Views to Sheets"):
        location = 0  # Adjust this value for your needs
        for view in views_for_sheet:
            add_view_to_sheet(selected_sheet, view, location)
            location += 50  # Increment location for next view (adjust as needed)
