# Import Revit API
from Autodesk.Revit.DB import Transaction, XYZ, Line, Arc, Curve, TextNote, ModelCurve, DetailCurve

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
    # Separate the curve and the elements to distribute
    selected_curve = None
    elements_to_distribute = []
    for element in selection:
        if isinstance(element, (ModelCurve, DetailCurve)):
            selected_curve = element.GeometryCurve
        else:
            elements_to_distribute.append(element)

    if selected_curve is None:
        print("No curve selected. Do nothing.")
    else:
        # Calculate the total length and the distance between each element
        total_length = selected_curve.Length
        num_gaps = len(elements_to_distribute) - 1
        parametric_distance = 1.0 / num_gaps  # Curve parameters range from 0 to 1

        # Start a new transaction
        with Transaction(doc, 'Distribute Elements Along Curve') as t:
            t.Start()

            # Distribute each selected element
            for i, element in enumerate(elements_to_distribute):
                parametric_position = i * parametric_distance
                target_point = selected_curve.Evaluate(parametric_position, True)
                if isinstance(element, TextNote):
                    # Handle TextNotes
                    element_location = element.Coord
                    new_location = XYZ(target_point.X, target_point.Y, element_location.Z)
                    element.Coord = new_location
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
