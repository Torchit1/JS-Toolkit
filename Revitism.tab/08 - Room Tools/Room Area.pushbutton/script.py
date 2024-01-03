from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, Element,
                               OverrideGraphicSettings, Color, Transaction, ElementId, XYZ)
from Autodesk.Revit.DB.Architecture import Room
from pyrevit import revit, DB

print("Code Explanation:")
print("This code checks each room in the Revit document against specified area criteria.")

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

print("\nStarting room check...")

rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

if not rooms:
    print("No rooms found in the document.")
else:
    print("Found {} rooms in the document.".format(len(rooms)))

criteria = {'Bed 1': 10, 'Bed': 9}
room_data = {}

try:
    for room in rooms:
        if isinstance(room, Room):
            room_name = Element.Name.GetValue(room)
            room_area = room.Area * 0.092903  # Adjust this conversion factor if necessary

            matched = False
            for room_type, min_area in criteria.items():
                if room_type.lower() in room_name.lower():
                    matched = True
                    room_data[room.Id] = (room_area, room_area >= min_area)
                    break
except Exception as e:
    print("Error: {}".format(e))

print("Room Check Summary:")
for id, (area, meets_criteria) in room_data.items():
    room = doc.GetElement(id)
    room_name = Element.Name.GetValue(room)
    if meets_criteria:
        print('Room Name: {}, Room Area: {:.2f} m2 - Meets criteria'.format(room_name, area))
    else:
        print('Room Name: {}, Room Area: {:.2f} m2 - Does not meet criteria'.format(room_name, area))

print("Room check completed.")
