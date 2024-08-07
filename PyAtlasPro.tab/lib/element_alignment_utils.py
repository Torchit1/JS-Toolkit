from Autodesk.Revit.DB import *
from pyrevit import revit, DB

doc = revit.doc
uidoc = revit.uidoc

def get_view_orientation_axis(view, direction):
    if direction in ['center-h', 'left', 'right']:
        if abs(view.RightDirection.X) > 0.9:
            return 'X'
        elif abs(view.RightDirection.Y) > 0.9:
            return 'Y'
        else:
            return 'Z'
    else:  # 'center-v', 'top', 'bottom'
        if abs(view.UpDirection.Z) > 0.9:
            return 'Z'
        elif abs(view.UpDirection.Y) > 0.9:
            return 'Y'
        else:
            return 'X'

def get_element_bbox_point(element, axis, direction):
    bbox = element.get_BoundingBox(None)  
    if not bbox:  
        bbox = element.get_BoundingBox(doc.ActiveView)
    if not bbox:
        #print("No bounding box found for element ID: " + str(element.Id.IntegerValue))
        return None
    
    if direction == 'center-h' or direction == 'center-v':
        point = (getattr(bbox.Min, axis) + getattr(bbox.Max, axis)) / 2.0
    elif direction in ['left', 'bottom']:
        point = getattr(bbox.Min, axis)
    else:  # 'right', 'top'
        point = getattr(bbox.Max, axis)
    #print("Bounding box point for element ID: {0} on axis {1} is {2}".format(element.Id.IntegerValue, axis, point))
    
    return point

def align_elements(doc, elements, direction):
    view = doc.ActiveView
    
     
    is_vertical_view = isinstance(view, ViewSection) or view.ViewType == ViewType.Elevation
    
    
    if is_vertical_view and direction in ['left', 'right']:
        direction = 'right' if direction == 'left' else 'left'
    
    
    axis = get_view_orientation_axis(view, direction)
    
    alignment_points = []
    for el in elements:
        point = get_element_bbox_point(el, axis, direction)
        if point is not None:
            alignment_points.append(point)

    if not alignment_points:
        #print("No valid points for alignment found.")
        return

    if direction in ['center-h', 'center-v']:
        target_point = sum(alignment_points) / len(alignment_points)
    else:
        target_point = min(alignment_points) if direction in ['left', 'bottom'] else max(alignment_points)
    
    #print("Target point for alignment on axis {0} is {1}".format(axis, target_point))

    with Transaction(doc, "Align Elements") as t:
        t.Start()
        for el in elements:
            element_point = get_element_bbox_point(el, axis, direction)
            if element_point is not None:
                delta = target_point - element_point
                move_vector = XYZ(delta if axis == 'X' else 0, delta if axis == 'Y' else 0, delta if axis == 'Z' else 0)
                ElementTransformUtils.MoveElement(doc, el.Id, move_vector)
                #print("Moved element ID: {0} with delta: {1}".format(el.Id.IntegerValue, delta))
        t.Commit()

    #print("Alignment completed successfully.")

def main():
    direction = "left"  # Example direction; can be "left", "right", "top", "bottom", "center-h", "center-v"
    selected_ids = revit.uidoc.Selection.GetElementIds()
    elements_str = ", ".join([str(id.IntegerValue) for id in selected_ids])
    #print("Selected element IDs: " + elements_str)
    elements = [doc.GetElement(id) for id in selected_ids]
    align_elements(doc, elements, direction)

if __name__ == "__main__":
    main()
