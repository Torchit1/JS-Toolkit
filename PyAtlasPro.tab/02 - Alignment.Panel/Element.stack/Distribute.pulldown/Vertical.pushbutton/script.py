# Import Revit API
from Autodesk.Revit.DB import Transaction, XYZ, Line, TextNote, LocationPoint, LocationCurve

# Import PyRevit
from pyrevit import revit, DB

# Get the current document
doc = revit.doc

# Get the selected elements
selection = revit.get_selection()

# Check if any elements are selected
if not selection or len(selection) < 3:
    print("Less than three elements selected. Do nothing.")
else:
    # Find the topmost and bottommost Y-coordinates among the selected elements
    topmost_y = None
    bottommost_y = None
    for element in selection:
        if isinstance(element, TextNote):
            bbox = element.BoundingBox[doc.ActiveView]
            y = (bbox.Min.Y + bbox.Max.Y) / 2
        else:
            element_location = element.Location
            if isinstance(element_location, LocationPoint):
                y = element_location.Point.Y
            elif isinstance(element_location, LocationCurve):
                y = element_location.Curve.GetEndPoint(0).Y
            else:
                continue  # Skip elements without a point or curve location

        if topmost_y is None or y > topmost_y:
            topmost_y = y
        if bottommost_y is None or y < bottommost_y:
            bottommost_y = y

    # Calculate the distance to distribute each element
    total_distance = topmost_y - bottommost_y
    num_gaps = len(selection) - 1
    distance_between = total_distance / num_gaps

    # Start a new transaction
    with Transaction(doc, 'Distribute Elements Vertically') as t:
        t.Start()

        # Distribute each selected element
        for i, element in enumerate(sorted(selection, key=lambda e: e.Location.Point.Y if isinstance(e.Location, LocationPoint) else e.Location.Curve.GetEndPoint(0).Y if isinstance(e.Location, LocationCurve) else 0)):
            target_y = bottommost_y + i * distance_between
            if isinstance(element, TextNote):
                bbox = element.BoundingBox[doc.ActiveView]
                center_bbox = (bbox.Min + bbox.Max) / 2
                offset = XYZ(0, target_y - center_bbox.Y, 0)
                element.Location.Move(offset)
            else:
                element_location = element.Location
                if isinstance(element_location, LocationPoint):
                    new_point = XYZ(element_location.Point.X, target_y, element_location.Point.Z)
                    element.Location.Point = new_point
                elif isinstance(element_location, LocationCurve):
                    start_point = element_location.Curve.GetEndPoint(0)
                    end_point = element_location.Curve.GetEndPoint(1)
                    new_start_point = XYZ(start_point.X, target_y, start_point.Z)
                    new_end_point = XYZ(end_point.X, target_y, end_point.Z)
                    element_location.Curve = Line.CreateBound(new_start_point, new_end_point)

        # Commit the transaction
        t.Commit()
