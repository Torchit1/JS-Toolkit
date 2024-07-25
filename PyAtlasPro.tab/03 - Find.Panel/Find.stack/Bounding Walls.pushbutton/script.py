from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, BuiltInParameter, ElementId
from System.Collections.Generic import List
from pyrevit import revit, DB

# Get the current document and active view
doc = revit.doc
active_view = doc.ActiveView

# Get all walls in the document
walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

# Start a new transaction
with Transaction(doc, 'Isolate Room-Bounding Walls') as t:
    t.Start()

    # List to store the Ids of room-bounding walls
    room_bounding_wall_ids = List[ElementId]()

    # Iterate over the walls
    for wall in walls:
        # Check if the wall is room-bounding
        is_room_bounding_param = wall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING)
        if is_room_bounding_param and is_room_bounding_param.AsInteger() == 1:
            # Add the Id of the room-bounding wall to the list
            room_bounding_wall_ids.Add(wall.Id)

    # Isolate the room-bounding walls in the active view
    active_view.IsolateElementsTemporary(room_bounding_wall_ids)

    # Commit the transaction
    t.Commit()
