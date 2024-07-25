# Import Revit API
from Autodesk.Revit.DB import Transaction, XYZ, Line
from math import pi, cos, sin

# Import PyRevit
from pyrevit import revit, DB

# Function to convert millimeters to feet
def mm_to_feet(value):
    return value * 0.00328084

# Get the current document
doc = revit.doc

# Get the selected elements
selection = revit.get_selection()

# Function to get the location point of an element
def get_location_point(element):
    element_location = element.Location
    if hasattr(element_location, "Point"):
        return element_location.Point
    elif hasattr(element_location, "Curve"):
        return element_location.Curve.GetEndPoint(0)
    else:
        return None

# Check if any elements are selected
if not selection or len(selection) < 2:
    print("Less than two elements selected. Do nothing.")
else:
    # Assume the first selected element is the center
    center_element = selection[0]
    center_point = get_location_point(center_element)
    if center_point is None:
        print("Center element has no point or curve location. Do nothing.")
    else:
        # Ask the user for the fixed distance (radius) in millimeters
        try:
            radius_mm = float(input("Enter the fixed distance (radius) for radial distribution in millimeters: "))
            radius = mm_to_feet(radius_mm)
        except ValueError:
            print("Invalid input. Please enter a numerical value for the radius.")
            exit()

        # Calculate the angular distance between each element
        total_angle = 2 * pi  # Full circle
        num_elements = len(selection) - 1  # Exclude the center element
        angle_between = total_angle / num_elements

        # Start a new transaction
        with Transaction(doc, 'Radial Distribution of Elements') as t:
            t.Start()

            # Distribute each selected element radially around the center
            for i, element in enumerate(selection[1:]):
                angle = i * angle_between
                element_point = get_location_point(element)
                if element_point is None:
                    continue  # Skip elements without a point or curve location

                # Calculate the new position
                target_point = XYZ(
                    center_point.X + radius * cos(angle),
                    center_point.Y + radius * sin(angle),
                    center_point.Z
                )

                # Move the element to the new position
                element.Location.Point = target_point

            # Commit the transaction
            t.Commit()
