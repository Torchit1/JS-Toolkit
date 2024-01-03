from pyrevit import revit, DB

def GetElementCenter(el):
    cen = el.Location.Point
    upper_limit = el.UpperLimit.Elevation
    limit_offset = el.LimitOffset
    z = upper_limit + (limit_offset / 2)
    cen = cen.Add(DB.XYZ(0, 0, z))
    return cen, upper_limit, limit_offset, z

def tag_all_rooms():
    rooms = DB.FilteredElementCollector(revit.doc)\
              .OfCategory(DB.BuiltInCategory.OST_Rooms)\
              .WhereElementIsNotElementType()\
              .ToElements()

    views = DB.FilteredElementCollector(revit.doc)\
              .OfClass(DB.View)\
              .WhereElementIsNotElementType()\
              .ToElements()
    views = [v for v in views if not v.IsTemplate and v.ViewType in [DB.ViewType.FloorPlan, DB.ViewType.CeilingPlan, DB.ViewType.Section, DB.ViewType.Elevation]]

    with revit.Transaction('Tag All Rooms in All Views'):
        for view in views:
            for el in rooms:
                room_center, upper_limit, limit_offset, z = GetElementCenter(el)

                if not room_center:
                    continue

                if isinstance(view, (DB.ViewSection, DB.ViewPlan)):
                    try:
                        room_tag = revit.doc.Create.NewRoomTag(
                            DB.LinkElementId(el.Id),
                            DB.UV(room_center.X, room_center.Y),
                            view.Id
                        )
                        if isinstance(view, DB.ViewSection):
                            room_tag.Location.Move(DB.XYZ(0, 0, z))
                    except Exception as e:
                        print("Error creating tag for element {}: {}".format(el.Id, str(e)))

# Execute the tag_all_rooms function
tag_all_rooms()
