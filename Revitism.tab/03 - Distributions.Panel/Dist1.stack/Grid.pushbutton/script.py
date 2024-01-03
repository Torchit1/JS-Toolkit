# Import Revit API
from Autodesk.Revit.DB import Transaction, XYZ, Line

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
    # Assume the first selected element is the starting point (top-left corner)
    start_element = selection[0]
    start_point = get_location_point(start_element)
    if start_point is None:
        print("Starting element has no point or curve location. Do nothing.")
    else:
        # Ask the user for the horizontal and vertical distances in millimeters
        try:
            h_distance_mm = float(input("Enter the horizontal distance between elements in millimeters: "))
            v_distance_mm = float(input("Enter the vertical distance between elements in millimeters: "))
            h_distance = mm_to_feet(h_distance_mm)
            v_distance = mm_to_feet(v_distance_mm)
        except ValueError:
            print("Invalid input. Please enter numerical values for the distances.")
            exit()

        # Calculate the number of rows and columns for the grid
        num_elements = len(selection) - 1  # Exclude the starting element
        num_rows = int(num_elements ** 0.5)
        num_columns = num_elements // num_rows + (1 if num_elements % num_rows > 0 else 0)

        # Start a new transaction
        with Transaction(doc, 'Grid Distribution of Elements') as t:
            t.Start()

            # Distribute each selected element in a grid pattern
            row = 0
            col = 0
            for element in selection[1:]:
                element_point = get_location_point(element)
                if element_point is None:
                    continue  # Skip elements without a point or curve location

                # Calculate the new position
                target_point = XYZ(
                    start_point.X + col * h_distance,
                    start_point.Y + row * v_distance,
                    start_point.Z
                )

                # Move the element to the new position
                element.Location.Point = target_point

                # Update row and column for the next element
                col += 1
                if col >= num_columns:
                    col = 0
                    row += 1

            # Commit the transaction
            t.Commit()
