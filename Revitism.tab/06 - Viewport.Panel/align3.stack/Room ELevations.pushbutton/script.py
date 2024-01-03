import clr
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.UI import TaskDialog
from pyrevit import revit, forms
from System import Guid

# Get the current document
doc = revit.doc

# Get all rooms in the document
rooms_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

# Filter rooms that are placed and have a location point
valid_rooms = [room for room in rooms_collector if room.Location is not None and isinstance(room, Room)]

# Check if there are valid rooms
if not valid_rooms:
    TaskDialog.Show('Error', 'No valid rooms found in the project.')
else:
    room_dict = {room.LookupParameter("Name").AsString(): room for room in valid_rooms if room.LookupParameter("Name").AsString() is not None}
    selected_room_name = forms.SelectFromList.show(sorted(room_dict.keys()), button_name='Select Room', multiselect=False)

    if selected_room_name:
        selected_room = room_dict[selected_room_name]
        view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType)
        view_family_type_id = None
        for vft in view_family_types:
            if vft.ViewFamily == ViewFamily.Elevation:
                view_family_type_id = vft.Id
                break

        if view_family_type_id is None:
            TaskDialog.Show('Error', 'No Elevation ViewFamilyType found in the project.')
        else:
            with Transaction(doc, 'Create Elevation Markers') as t:
                t.Start()
                try:
                    location_point = selected_room.Location.Point
                    elevation_marker = ElevationMarker.CreateElevationMarker(doc, view_family_type_id, location_point, 100)
                    
                    suffixes = ['a', 'b', 'c', 'd']
                    for i in range(0, 4):
                        elevation = elevation_marker.CreateElevation(doc, doc.ActiveView.Id, i)
                        elevation_name = "{} - Elevation - {}".format(selected_room_name, suffixes[i])
                        elevation.Name = elevation_name
                        
                except Exception as e:
                    print("Could not create elevation for room {}: {}".format(selected_room.Id.IntegerValue, str(e)))
                t.Commit()
    else:
        TaskDialog.Show('Error', 'No room selected.')