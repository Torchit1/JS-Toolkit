import clr
import pyrevit

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, View, ViewType, Level, DatumEnds

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
        levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

        level_dict = {l.Name: l for l in levels}

        selected_level_names = forms.SelectFromList.show(sorted(level_dict.keys()), button_name='Select Levels', multiselect=True, title='Select Levels')

        if selected_level_names:
            action_dict = {
                'Turn On All Level Heads': 'Turn On All',
                'Turn Off All Level Heads': 'Turn Off All',
                'Turn On Left Level Heads': 'Turn On Left',
                'Turn Off Left Level Heads': 'Turn Off Left',
                'Turn On Right Level Heads': 'Turn On Right',
                'Turn Off Right Level Heads': 'Turn Off Right'
            }
            action = forms.CommandSwitchWindow.show(action_dict.keys(), message='Choose action:')
            
            if action:
                with Transaction(doc, '{} Level Heads'.format(action_dict[action])) as t:
                    t.Start()
                    
                    for view_name in selected_view_names:
                        view = view_dict[view_name]
                        
                        levels_to_adjust = [level_dict[level_name] for level_name in selected_level_names]
                        
                        for level in levels_to_adjust:
                            try:
                                if 'All' in action or 'Left' in action:
                                    if 'On' in action:
                                        level.ShowBubbleInView(DatumEnds.End0, view)
                                    else:
                                        level.HideBubbleInView(DatumEnds.End0, view)
                            except:
                                pass
                            
                            try:
                                if 'All' in action or 'Right' in action:
                                    if 'On' in action:
                                        level.ShowBubbleInView(DatumEnds.End1, view)
                                    else:
                                        level.HideBubbleInView(DatumEnds.End1, view)
                            except:
                                pass
                    
                    t.Commit()
