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
    # Find the leftmost and rightmost X-coordinates among the selected elements
    leftmost_x = None
    rightmost_x = None
    for element in selection:
        if isinstance(element, TextNote):
            bbox = element.BoundingBox[doc.ActiveView]
            x = (bbox.Min.X + bbox.Max.X) / 2
        else:
            element_location = element.Location
            if isinstance(element_location, LocationPoint):
                x = element_location.Point.X
            elif isinstance(element_location, LocationCurve):
                x = element_location.Curve.GetEndPoint(0).X
            else:
                continue  # Skip elements without a point or curve location

        if leftmost_x is None or x < leftmost_x:
            leftmost_x = x
        if rightmost_x is None or x > rightmost_x:
            rightmost_x = x

    # Calculate the distance to distribute each element
    total_distance = rightmost_x - leftmost_x
    num_gaps = len(selection) - 1
    distance_between = total_distance / num_gaps

    # Start a new transaction
    with Transaction(doc, 'Distribute Elements Horizontally') as t:
        t.Start()

        # Distribute each selected element
        for i, element in enumerate(sorted(selection, key=lambda e: e.Location.Point.X if isinstance(e.Location, LocationPoint) else e.Location.Curve.GetEndPoint(0).X if isinstance(e.Location, LocationCurve) else 0)):
            target_x = leftmost_x + i * distance_between
            if isinstance(element, TextNote):
                bbox = element.BoundingBox[doc.ActiveView]
                center_bbox = (bbox.Min + bbox.Max) / 2
                offset = XYZ(target_x - center_bbox.X, 0, 0)
                element.Location.Move(offset)
            else:
                element_location = element.Location
                if isinstance(element_location, LocationPoint):
                    new_point = XYZ(target_x, element_location.Point.Y, element_location.Point.Z)
                    element.Location.Point = new_point
                elif isinstance(element_location, LocationCurve):
                    start_point = element_location.Curve.GetEndPoint(0)
                    end_point = element_location.Curve.GetEndPoint(1)
                    new_start_point = XYZ(target_x, start_point.Y, start_point.Z)
                    new_end_point = XYZ(target_x, end_point.Y, end_point.Z)
                    element_location.Curve = Line.CreateBound(new_start_point, new_end_point)

        # Commit the transaction
        t.Commit()
