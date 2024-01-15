from pyrevit import revit, DB, forms
from Autodesk.Revit.DB import *

def GetElementCenter(el):
    cen = el.Location.Point
    upper_limit = el.UpperLimit.Elevation
    limit_offset = el.LimitOffset
    z = upper_limit + (limit_offset / 2)
    cen = cen.Add(DB.XYZ(0, 0, z))
    return cen, upper_limit, limit_offset, z

def collect_existing_room_tags(doc):
    existing_tags = {}
    room_tags = FilteredElementCollector(doc).OfClass(DB.SpatialElementTag).ToElements()
    for tag in room_tags:
        room_id = tag.Room.Id.IntegerValue
        view_id = tag.OwnerViewId.IntegerValue
        if room_id not in existing_tags:
            existing_tags[room_id] = set()
        existing_tags[room_id].add(view_id)
    return existing_tags

def select_views(doc):
    all_views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()
    target_view_types = [ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]
    available_views = [v for v in all_views if v.ViewType in target_view_types and not v.IsTemplate]
    view_names = sorted([v.Name for v in available_views])
    selected_view_names = forms.SelectFromList.show(view_names, multiselect=True, title='Select Views', button_name='Select')
    if selected_view_names is None:
        raise SystemExit
    return [v for v in available_views if v.Name in selected_view_names]

def tag_all_rooms(selected_views):
    doc = revit.doc
    rooms = FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
    existing_tags = collect_existing_room_tags(doc)

    with revit.Transaction('Tag All Rooms in Selected Views'):
        for view in selected_views:
            for el in rooms:
                if el.Id.IntegerValue in existing_tags and view.Id.IntegerValue in existing_tags[el.Id.IntegerValue]:
                    continue  # Skip if room is already tagged in this view

                room_center, upper_limit, limit_offset, z = GetElementCenter(el)
                if not room_center:
                    continue

                if isinstance(view, (DB.ViewSection, DB.ViewPlan)):
                    try:
                        room_tag = doc.Create.NewRoomTag(
                            DB.LinkElementId(el.Id),
                            DB.UV(room_center.X, room_center.Y),
                            view.Id
                        )
                        if isinstance(view, DB.ViewSection):
                            room_tag.Location.Move(DB.XYZ(0, 0, z))
                    except Exception as e:
                        print("Error creating tag for room {}: {}".format(el.Id, str(e)))

# Main execution
try:
    selected_views = select_views(revit.doc)
    if selected_views:
        tag_all_rooms(selected_views)
except SystemExit:
    pass
except Exception as e:
    print("Error: " + str(e))
