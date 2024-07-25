# Import Revit API
from Autodesk.Revit.DB import Transaction, XYZ, Line, Arc, Curve, ModelCurve, DetailCurve, TextNote, View
from math import pi, cos, sin

# Import PyRevit
from pyrevit import revit, DB

# Get the current document
doc = revit.doc

# Get the selected elements
selection = revit.get_selection()

# Get the active view (you may need to adjust this to get the correct view)
active_view = doc.ActiveView

# Check if any elements are selected
if not selection or len(selection) < 3:
    print("Less than three elements selected. Do nothing.")
else:
    # Separate the circle and the elements to distribute
    selected_circle = None
    elements_to_distribute = []
    for element in selection:
        if isinstance(element, (ModelCurve, DetailCurve)) and isinstance(element.GeometryCurve, Arc) and element.GeometryCurve.IsBound == False:
            selected_circle = element.GeometryCurve
        else:
            elements_to_distribute.append(element)

    if selected_circle is None:
        print("No circle selected. Do nothing.")
    else:
        # Get the center and radius of the circle
        center = selected_circle.Center
        radius = selected_circle.Radius

        # Calculate the angular distance between each element
        total_angle = 2 * pi  # Full circle
        num_gaps = len(elements_to_distribute)
        angle_between = total_angle / num_gaps

        # Start a new transaction
        with Transaction(doc, 'Distribute Elements Along Circle') as t:
            t.Start()

            # Distribute each selected element
            for i, element in enumerate(elements_to_distribute):
                # Start from the top of the circle (pi/2 radians or 90 degrees)
                angle = pi / 2 + i * angle_between
                target_point = XYZ(center.X + radius * cos(angle), center.Y + radius * sin(angle), center.Z)
                if isinstance(element, TextNote):
                    # Handle TextNotes
                    bbox = element.get_BoundingBox(active_view)
                    if bbox:
                        center_bbox = (bbox.Min + bbox.Max) / 2
                        offset = target_point - center_bbox
                        element.Location.Move(offset)
                else:
                    element_location = element.Location
                    if hasattr(element_location, "Point"):
                        new_point = XYZ(target_point.X, target_point.Y, element_location.Point.Z)
                        element.Location.Point = new_point
                    elif hasattr(element_location, "Curve"):
                        start_point = element_location.Curve.GetEndPoint(0)
                        end_point = element_location.Curve.GetEndPoint(1)
                        new_start_point = XYZ(target_point.X, target_point.Y, start_point.Z)
                        new_end_point = XYZ(target_point.X, target_point.Y, end_point.Z)
                        element_location.Curve = Line.CreateBound(new_start_point, new_end_point)

            # Commit the transaction
            t.Commit()
