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
    # Find the middle X-coordinate among the selected elements
    total_x = 0
    valid_elements_count = 0
    for element in selection:
        element_point = get_location_point(element)
        if element_point is not None:
            total_x += element_point.X
            valid_elements_count += 1

    if valid_elements_count == 0:
        print("No valid location points found among the selected elements. Do nothing.")
    else:
        middle_x = total_x / valid_elements_count

        # Start a new transaction
        with Transaction(doc, 'Horizontal Middle Align Elements') as t:
            t.Start()

            # Align each selected element to the middle X-coordinate
            for element in selection:
                if isinstance(element, TextNote):
                    element.Coord = XYZ(middle_x, element.Coord.Y, element.Coord.Z)
                elif isinstance(element, IndependentTag):
                    element.LeaderEnd = XYZ(middle_x, element.LeaderEnd.Y, element.LeaderEnd.Z)
                elif isinstance(element, SpotDimension):
                    offset_x = middle_x - get_location_point(element).X
                    new_bend = XYZ(element.BendPoint.X + offset_x, element.BendPoint.Y, element.BendPoint.Z)
                    new_end = XYZ(element.EndPoint.X + offset_x, element.EndPoint.Y, element.EndPoint.Z)
                    element.BendPoint = new_bend
                    element.EndPoint = new_end
                elif isinstance(element, Viewport):
                    current_box_center = element.GetBoxCenter()
                    offset_x = middle_x - current_box_center.X
                    new_box_center = XYZ(current_box_center.X + offset_x, current_box_center.Y, current_box_center.Z)
                    element.SetBoxCenter(new_box_center)
                elif isinstance(element, Wall):
                    offset = get_location_point(element).X - middle_x
                    element.Location.Move(XYZ(-offset, 0, 0))
                elif isinstance(element, FamilyInstance) and hasattr(element.Location, 'Point'):
                    offset = element.Location.Point.X - middle_x
                    element.Location.Move(XYZ(-offset, 0, 0))
                else:
                    print("Element of type {} not handled".format(type(element)))

            # Commit the transaction
            t.Commit()
