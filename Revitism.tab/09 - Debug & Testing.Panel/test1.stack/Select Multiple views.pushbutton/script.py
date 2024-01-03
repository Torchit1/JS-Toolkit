from Autodesk.Revit.DB import FilteredElementCollector, View, ViewSheet, ViewType
from pyrevit import revit, DB, forms

# Get the active document (the open project in Revit)
doc = revit.doc

def list_views(doc):
    """
    List views in the active Revit project that can be placed on sheets,
    grouped by view type, and indicate if they are already placed on sheets.
    """
    # Create a collector instance for collecting all views
    views_collector = FilteredElementCollector(doc).OfClass(View)

    # Dictionary to store views grouped by type
    views_by_type = {}

    # Iterate over views, group by type and add their names to the dictionary
    for view in views_collector:
        # Exclude system views and non-user-creatable views
        if view.ViewType not in [ViewType.DrawingSheet, ViewType.ProjectBrowser, ViewType.SystemBrowser] and \
           not view.IsTemplate and \
           view.ViewType != DB.ViewType.Undefined:
            view_type = view.ViewType
            view_label = view.Name

            # Check if the view is placed on a sheet
            if view.OwnerViewId != DB.ElementId.InvalidElementId:
                sheet = doc.GetElement(view.OwnerViewId)
                if isinstance(sheet, ViewSheet):
                    view_label += " [On Sheet: {}]".format(sheet.SheetNumber)

            if view_type not in views_by_type:
                views_by_type[view_type] = []
            views_by_type[view_type].append(view_label)

    # Sort and format view names
    sorted_views = []
    for view_type, view_labels in views_by_type.items():
        view_labels.sort()
        sorted_views.extend(["{}: {}".format(view_type, label) for label in view_labels])

    return sorted_views

# Get the sorted list of views, grouped by view type
views_list = list_views(doc)

# Show the selection box with multiselect enabled
selected_views = forms.SelectFromList.show(views_list, title="Select Views", multiselect=True)

# Do something with the selected views
if selected_views:
    selected_views_message = "\n".join(selected_views)
    alert_message = "You selected:\n{}".format(selected_views_message)
    forms.alert(alert_message)
