import clr
import pyrevit

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, View, ViewType, Grid, DatumEnds

from pyrevit import forms

doc = pyrevit.revit.doc

sel_sheets = forms.select_sheets(title='Select Sheets')

if sel_sheets:
    views = []
    for sheet in sel_sheets:
        for view_id in sheet.GetAllPlacedViews():
            views.append(doc.GetElement(view_id))
            
    valid_view_types = set([ViewType.Section, ViewType.Elevation, ViewType.ThreeD, ViewType.FloorPlan])
    valid_views = [v for v in views if v.ViewType in valid_view_types and not v.IsTemplate and v.CanBePrinted]

    view_dict = {v.Name: v for v in valid_views}

    selected_view_names = forms.SelectFromList.show(sorted(view_dict.keys()), button_name='Select Views', multiselect=True, title='Select Views from Sheets')

    if selected_view_names:
        grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

        grid_dict = {g.Name: g for g in grids}

        selected_grid_names = forms.SelectFromList.show(sorted(grid_dict.keys()), button_name='Select Grids', multiselect=True, title='Select Grids')

        if selected_grid_names:
            action_dict = {
                'Turn On Selected Grid Heads': 'Turn On',
                'Turn Off Selected Grid Heads': 'Turn Off',
                'Turn On A-Side Grid Heads': 'Turn On A',
                'Turn Off A-Side Grid Heads': 'Turn Off A',
                'Turn On B-Side Grid Heads': 'Turn On B',
                'Turn Off B-Side Grid Heads': 'Turn Off B'
            }
            action = forms.CommandSwitchWindow.show(action_dict.keys(), message='Choose action:')
            
            if action:
                with Transaction(doc, '{} Grid Heads'.format(action_dict[action])) as t:
                    t.Start()
                    
                    for view_name in selected_view_names:
                        view = view_dict[view_name]
                        
                        grids_to_adjust = [grid_dict[grid_name] for grid_name in selected_grid_names]
                        
                        for grid in grids_to_adjust:
                            if grid.CanBeVisibleInView(view):
                                if 'On' in action:
                                    if 'A' in action:
                                        grid.ShowBubbleInView(DatumEnds.End0, view)
                                    elif 'B' in action:
                                        grid.ShowBubbleInView(DatumEnds.End1, view)
                                    else:
                                        grid.ShowBubbleInView(DatumEnds.End0, view)
                                        grid.ShowBubbleInView(DatumEnds.End1, view)
                                else:
                                    if 'A' in action:
                                        grid.HideBubbleInView(DatumEnds.End0, view)
                                    elif 'B' in action:
                                        grid.HideBubbleInView(DatumEnds.End1, view)
                                    else:
                                        grid.HideBubbleInView(DatumEnds.End0, view)
                                        grid.HideBubbleInView(DatumEnds.End1, view)
                    
                    t.Commit()
