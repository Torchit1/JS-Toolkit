# Import Revit API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId, LocationCurve, Transaction
from System.Collections.Generic import List

# Import PyRevit
from pyrevit import revit, DB

# Get the current document
doc = revit.doc

# Get the active view
active_view = doc.ActiveView

# Define a tolerance for considering a wall as vertical or horizontal
tolerance = 1e-3

# Start a new transaction
with Transaction(doc, 'Isolate Non-Vertical/Non-Horizontal Walls') as t:
    t.Start()

    # List to store the Ids of non-vertical/non-horizontal walls
    non_vertical_horizontal_wall_ids = List[ElementId]()

    # Collect all walls in the active view
    all_walls = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

    # Iterate over all walls in the active view
    for wall in all_walls:
        # Get the wall's location curve
        location_curve = wall.Location
        if isinstance(location_curve, LocationCurve):
            # Get the start and end points of the location curve
            start_point = location_curve.Curve.GetEndPoint(0)
            end_point = location_curve.Curve.GetEndPoint(1)
            
            # Check if the wall is not vertical or horizontal within the tolerance
            if not (abs(start_point.X - end_point.X) < tolerance or abs(start_point.Y - end_point.Y) < tolerance):
                # Add the Id of the non-vertical/non-horizontal wall to the list
                non_vertical_horizontal_wall_ids.Add(wall.Id)

    # Isolate the non-vertical/non-horizontal walls in the active view
    active_view.IsolateElementsTemporary(non_vertical_horizontal_wall_ids)

    # Commit the transaction
    t.Commit()
