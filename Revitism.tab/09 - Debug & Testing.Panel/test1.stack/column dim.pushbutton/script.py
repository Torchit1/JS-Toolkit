import clr
import math

# Import RevitAPI
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, XYZ,
                               Line, Transaction, DetailLine, ViewDetailLevel)

# Set the active Revit application and document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = uidoc.ActiveView

# Function to convert 3D point to 2D
def to_2d(point):
    return XYZ(point.X, point.Y, 0)

# Function to calculate distance between two points
def distance(pt1, pt2):
    return math.sqrt((pt1.X - pt2.X)**2 + (pt1.Y - pt2.Y)**2)

# Function to find the closest point on a line to another point
def closest_point_on_line(line_start, line_end, point):
    line_vec = line_end - line_start
    point_vec = point - line_start
    line_length = line_vec.GetLength()
    line_unit_vec = line_vec / line_length
    projected_length = point_vec.DotProduct(line_unit_vec)
    projected_length = max(0, min(line_length, projected_length))  # Clamp to line ends
    return line_start + line_unit_vec * projected_length

# Collect all grid lines in the active view
grids = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

# Get 2D lines from grid lines
grid_lines = []
for grid in grids:
    curve = grid.Curve
    start = to_2d(curve.GetEndPoint(0))
    end = to_2d(curve.GetEndPoint(1))
    grid_lines.append((grid, start, end))

# Collect all structural columns in the active view
columns = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()

# Start a transaction to create detail lines
with Transaction(doc, 'Create Detail Lines') as t:
    t.Start()
    
    for column in columns:
        location = column.Location
        if location:
            column_point = to_2d(location.Point)
            
            # Find the closest horizontal and vertical grid lines
            horz_grid = min([g for g in grid_lines if g[0].Name.isalpha()], key=lambda g: distance(column_point, g[1]))
            vert_grid = min([g for g in grid_lines if g[0].Name.isdigit()], key=lambda g: distance(column_point, g[1]))
            
            # Debugging prints
            print("horz_grid type:", type(horz_grid[0]), "value:", horz_grid[0])
            print("vert_grid type:", type(vert_grid[0]), "value:", vert_grid[0])
            
            # Find closest points on the grid lines and create detail lines
            closest_horz_point = closest_point_on_line(horz_grid[1], horz_grid[2], column_point)
            closest_vert_point = closest_point_on_line(vert_grid[1], vert_grid[2], column_point)
            horz_line = Line.CreateBound(column_point, closest_horz_point)
            vert_line = Line.CreateBound(column_point, closest_vert_point)
            
            # Debugging prints
            print("horz_line:", horz_line)
            print("vert_line:", vert_line)
            
            doc.Create.NewDetailCurve(view, horz_line)
            doc.Create.NewDetailCurve(view, vert_line)

    t.Commit()
