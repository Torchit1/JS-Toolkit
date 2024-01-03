# Import Revit API
from Autodesk.Revit.DB import Transaction, XYZ

# Import PyRevit
from pyrevit import revit, DB

# Golden Ratio
phi = 1.618033988749895

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
    # Assume the first selected element is the starting point
    start_element = selection[0]
    start_point = get_location_point(start_element)
    if start_point is None:
        print("Starting element has no point or curve location. Do nothing.")
    else:
        # Ask the user for the initial distance in millimeters
        try:
            initial_distance_mm = float(input("Enter the initial distance for golden ratio distribution in millimeters: "))
            initial_distance = mm_to_feet(initial_distance_mm)
        except ValueError:
            print("Invalid input. Please enter a numerical value for the initial distance.")
            exit()

        # Start a new transaction
        with Transaction(doc, 'Golden Ratio Distribution of Elements') as t:
            t.Start()

            # Distribute each selected element based on the golden ratio
            current_distance = initial_distance
            for element in selection[1:]:
                element_point = get_location_point(element)
                if element_point is None:
                    continue  # Skip elements without a point or curve location

                # Calculate the new position
                target_point = XYZ(
                    start_point.X + current_distance,
                    start_point.Y,
                    start_point.Z
                )

                # Move the element to the new position
                element.Location.Point = target_point

                # Update the distance for the next element based on the golden ratio
                current_distance *= phi

            # Commit the transaction
            t.Commit()
