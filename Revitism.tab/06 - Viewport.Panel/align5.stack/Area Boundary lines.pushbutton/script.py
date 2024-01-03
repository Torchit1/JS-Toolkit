import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Start a transaction
t = Transaction(doc, 'Create and Move Area Boundaries')
t.Start()

try:
    if not isinstance(uidoc.ActiveView, ViewPlan) or uidoc.ActiveView.AreaScheme is None:
        raise Exception("The active view must be an AreaPlan view to create area boundaries.")
    
    walls = FilteredElementCollector(doc, uidoc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    sketch_plane = uidoc.ActiveView.SketchPlane
    
    if sketch_plane is None:
        raise Exception("Active view must have an active SketchPlane to create ModelCurves.")
    
    # Create an Area Boundary Line for each wall
    for wall in walls:
        wall_type_id = wall.GetTypeId()
        wall_type = doc.GetElement(wall_type_id)

        if wall_type is None:
            print("Skipping wall " + str(wall.Id.IntegerValue) + " due to missing wall type.")
            continue
        
        width_param = wall_type.get_Parameter(BuiltInParameter.WALL_ATTR_WIDTH_PARAM)

        if width_param is None:
            print("Width parameter not found for wall type " + str(wall_type_id.IntegerValue) + ". Skipping this wall.")
            continue
        
        width = width_param.AsDouble()
        
        # Get the wall's location curve
        location_curve = wall.Location.Curve
        
        # Debugging: Print start and end points
        print("\nWall ID: {}".format(wall.Id))
        print("Original Start Point: {}".format(location_curve.GetEndPoint(0)))
        print("Original End Point: {}".format(location_curve.GetEndPoint(1)))
        
        # Determine whether the line is horizontal or vertical
        start_point = location_curve.GetEndPoint(0)
        end_point = location_curve.GetEndPoint(1)
        
        # Check if horizontal or vertical
        is_horizontal = abs(start_point.Y - end_point.Y) < 0.001  # tolerance for floating-point comparison
        is_vertical = abs(start_point.X - end_point.X) < 0.001  # tolerance for floating-point comparison
        
        # Check if it is a bottom or left wall by comparing Y or X values of the start and end points
        if is_horizontal:
            extend_direction = XYZ.BasisX if start_point.X < end_point.X else XYZ.BasisX.Negate()
        elif is_vertical:
            extend_direction = XYZ.BasisY if start_point.Y < end_point.Y else XYZ.BasisY.Negate()
        else:
            extend_direction = (end_point - start_point).Normalize()
        
        # Offset the curve by half the width of the wall
        offset_curve = location_curve.CreateOffset(width/2, XYZ.BasisZ)
        
        # Create a line extended at both ends
        extended_curve = Line.CreateBound(
            offset_curve.GetEndPoint(0) - extend_direction * (width / 2), 
            offset_curve.GetEndPoint(1) + extend_direction * (width / 2)
        )
        
        # Create a new area boundary line
        area_boundary_line = doc.Create.NewAreaBoundaryLine(sketch_plane, extended_curve, uidoc.ActiveView)
    
    t.Commit()
    print('Area boundary lines created and moved successfully.')
except Exception as e:
    t.RollBack()
    print('Error:', str(e))
