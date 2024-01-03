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
    # Find the middle Y-coordinate among the selected elements
    total_y = 0
    valid_elements_count = 0
    for element in selection:
        element_point = get_location_point(element)
        if element_point is not None:
            total_y += element_point.Y
            valid_elements_count += 1

    if valid_elements_count == 0:
        print("No valid location points found among the selected elements. Do nothing.")
    else:
        middle_y = total_y / valid_elements_count

        # Start a new transaction
        with Transaction(doc, 'Vertical Middle Align Elements') as t:
            t.Start()

            # Align each selected element to the middle Y-coordinate
            for element in selection:
                if isinstance(element, TextNote):
                    element.Coord = XYZ(element.Coord.X, middle_y, element.Coord.Z)
                elif isinstance(element, IndependentTag):
                    element.LeaderEnd = XYZ(element.LeaderEnd.X, middle_y, element.LeaderEnd.Z)
                elif isinstance(element, SpotDimension):
                    offset_y = middle_y - get_location_point(element).Y
                    new_bend = XYZ(element.BendPoint.X, element.BendPoint.Y + offset_y, element.BendPoint.Z)
                    new_end = XYZ(element.EndPoint.X, element.EndPoint.Y + offset_y, element.EndPoint.Z)
                    element.BendPoint = new_bend
                    element.EndPoint = new_end
                elif isinstance(element, Viewport):
                    current_box_center = element.GetBoxCenter()
                    offset_y = middle_y - current_box_center.Y
                    new_box_center = XYZ(current_box_center.X, current_box_center.Y + offset_y, current_box_center.Z)
                    element.SetBoxCenter(new_box_center)
                elif isinstance(element, Wall):
                    offset = get_location_point(element).Y - middle_y
                    element.Location.Move(XYZ(0, -offset, 0))
                elif isinstance(element, FamilyInstance) and hasattr(element.Location, 'Point'):
                    offset = element.Location.Point.Y - middle_y
                    element.Location.Move(XYZ(0, -offset, 0))
                else:
                    print("Element of type {} not handled".format(type(element)))

            # Commit the transaction
            t.Commit()
