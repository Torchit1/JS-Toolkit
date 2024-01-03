from Autodesk.Revit.DB import Transaction, XYZ, TextNote, IndependentTag, SpotDimension, Viewport, Wall, FamilyInstance
from pyrevit import revit, DB

# Get the current document
doc = revit.doc

# Get the selected elements
selection = revit.get_selection()

# Function to get the location point of an element
def get_location_point(element):
    if isinstance(element, TextNote):
        return element.Coord
    elif isinstance(element, IndependentTag):
        return element.LeaderEnd
    elif isinstance(element, SpotDimension):
        return element.Origin
    elif isinstance(element, Viewport):
        return element.GetBoxCenter()
    elif isinstance(element, Wall):
        return element.Location.Curve.GetEndPoint(0)
    elif isinstance(element, FamilyInstance):
        return element.Location.Point if hasattr(element.Location, 'Point') else None
    else:
        return None

# Check if any elements are selected
if not selection or len(selection) < 2:
    print("Less than two elements selected. Do nothing.")
else:
    # Find the rightmost point among the selected elements
    rightmost_point = None
    for element in selection:
        element_point = get_location_point(element)
        if element_point is not None:
            if rightmost_point is None or element_point.X > rightmost_point.X:
                rightmost_point = element_point

    if rightmost_point is None:
        print("No valid location points found among the selected elements. Do nothing.")
    else:
        # Start a new transaction
        with Transaction(doc, 'Right Align Elements') as t:
            t.Start()

            # Align each selected element to the rightmost point
            for element in selection:
                if isinstance(element, TextNote):
                    element.Coord = XYZ(rightmost_point.X, element.Coord.Y, element.Coord.Z)
                elif isinstance(element, IndependentTag):
                    element.LeaderEnd = XYZ(rightmost_point.X, element.LeaderEnd.Y, element.LeaderEnd.Z)
                elif isinstance(element, SpotDimension):
                    offset_x = rightmost_point.X - get_location_point(element).X
                    new_bend = XYZ(element.BendPoint.X + offset_x, element.BendPoint.Y, element.BendPoint.Z)
                    new_end = XYZ(element.EndPoint.X + offset_x, element.EndPoint.Y, element.EndPoint.Z)
                    element.BendPoint = new_bend
                    element.EndPoint = new_end
                elif isinstance(element, Viewport):
                    current_box_center = element.GetBoxCenter()
                    offset_x = rightmost_point.X - current_box_center.X
                    new_box_center = XYZ(current_box_center.X + offset_x, current_box_center.Y, current_box_center.Z)
                    element.SetBoxCenter(new_box_center)
                elif isinstance(element, Wall):
                    offset = get_location_point(element).X - rightmost_point.X
                    element.Location.Move(XYZ(-offset, 0, 0))
                elif isinstance(element, FamilyInstance) and hasattr(element.Location, 'Point'):
                    offset = element.Location.Point.X - rightmost_point.X
                    element.Location.Move(XYZ(-offset, 0, 0))
                else:
                    pass  # Replace 'pass' with actual logic for handling other element types

            # Commit the transaction
            t.Commit()
