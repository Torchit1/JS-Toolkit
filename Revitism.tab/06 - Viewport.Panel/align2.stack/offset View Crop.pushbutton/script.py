from Autodesk.Revit.DB import Transaction, FilteredElementCollector, BuiltInCategory, ViewSection, XYZ, ViewType
from pyrevit import revit, forms

doc = revit.doc

# Offset value in feet (assuming you are working in millimeters, adjust as needed)
offset = 300 * 0.00328084  # Conversion factor from mm to feet

# Get all ViewSections in the document
views_collector = FilteredElementCollector(doc).OfClass(ViewSection).WhereElementIsNotElementType().ToElements()

# Filter ViewSections that are Elevation views
elevation_views = [view for view in views_collector if view.ViewType == ViewType.Elevation]

# Check if there are valid Elevation views
if not elevation_views:
    forms.alert('Error', 'No Elevation views found in the project.')
else:
    view_dict = {view.Name: view for view in elevation_views}
    selected_view_names = forms.SelectFromList.show(sorted(view_dict.keys()), button_name='Select View', multiselect=True)

    if selected_view_names:
        with Transaction(doc, 'Adjust Crop Box') as t:
            t.Start()
            for view_name in selected_view_names:
                selected_view = view_dict[view_name]
                
                # Get the crop box of the selected view
                crop_box = selected_view.CropBox
                
                # Get the min and max XYZ values of the crop box
                min_point = crop_box.Min
                max_point = crop_box.Max
                
                # Adjust each side of the crop box
                new_min_point = XYZ(min_point.X - offset, min_point.Y - offset, min_point.Z)
                new_max_point = XYZ(max_point.X + offset, max_point.Y + offset, max_point.Z)
                
                # Set the new min and max XYZ values back to the crop box
                crop_box.Min = new_min_point
                crop_box.Max = new_max_point
                
                # Set the adjusted crop box back to the selected view
                selected_view.CropBox = crop_box
            t.Commit()
    else:
        forms.alert('Warning', 'No view selected.')
