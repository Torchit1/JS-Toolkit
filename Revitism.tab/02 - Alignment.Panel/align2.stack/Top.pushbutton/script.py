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
    # Find the highest point among the selected elements
    highest_point = None
    for element in selection:
        element_point = get_location_point(element)
        if element_point is not None:
            if highest_point is None or element_point.Y > highest_point.Y:
                highest_point = element_point

    if highest_point is None:
        print("No valid location points found among the selected elements. Do nothing.")
    else:
        # Start a new transaction
        with Transaction(doc, 'Top Align Elements') as t:
            t.Start()

            # Align each selected element to the highest point
            for element in selection:
                if isinstance(element, TextNote):
                    element.Coord = XYZ(element.Coord.X, highest_point.Y, element.Coord.Z)
                elif isinstance(element, IndependentTag):
                    element.LeaderEnd = XYZ(element.LeaderEnd.X, highest_point.Y, element.LeaderEnd.Z)
                elif isinstance(element, SpotDimension):
                    offset_y = highest_point.Y - get_location_point(element).Y
                    new_bend = XYZ(element.BendPoint.X, element.BendPoint.Y + offset_y, element.BendPoint.Z)
                    new_end = XYZ(element.EndPoint.X, element.EndPoint.Y + offset_y, element.EndPoint.Z)
                    element.BendPoint = new_bend
                    element.EndPoint = new_end
                elif isinstance(element, Viewport):
                    current_box_center = element.GetBoxCenter()
                    offset_y = highest_point.Y - current_box_center.Y
                    new_box_center = XYZ(current_box_center.X, current_box_center.Y + offset_y, current_box_center.Z)
                    element.SetBoxCenter(new_box_center)
                elif isinstance(element, Wall):
                    offset = get_location_point(element).Y - highest_point.Y
                    element.Location.Move(XYZ(0, -offset, 0))
                elif isinstance(element, FamilyInstance) and hasattr(element.Location, 'Point'):
                    offset = element.Location.Point.Y - highest_point.Y
                    element.Location.Move(XYZ(0, -offset, 0))
                else:
                    print("Element of type {} not handled".format(type(element)))


            # Commit the transaction
            t.Commit()
