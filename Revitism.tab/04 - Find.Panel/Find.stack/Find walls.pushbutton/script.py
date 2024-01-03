from pyrevit import revit, DB, script
from System.Drawing import Color

def is_whole_number(length):
    return abs(length - round(length)) < 0.01

doc = revit.doc
uidoc = revit.uidoc
current_view = uidoc.ActiveView
output = script.get_output()

filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Walls)
walls = DB.FilteredElementCollector(doc, current_view.Id).WherePasses(filter).WhereElementIsNotElementType()

all_walls_info = []
non_whole_walls_info = []
output.indeterminate_progress(True)

with DB.Transaction(doc, "Highlight Non-Whole Length Walls") as t:
    t.Start()
    output.update_progress

    for wall in walls:
        wall_params = {}
        for param in wall.Parameters:
            if param.HasValue:
                param_name = param.Definition.Name  # Use parameter name directly
                wall_params[param_name] = param.AsString() or param.AsValueString()

        length_param = wall.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH)
        if length_param and length_param.HasValue:
            length = length_param.AsDouble()
            length_mm = DB.UnitUtils.ConvertFromInternalUnits(length, DB.DisplayUnitType.DUT_MILLIMETERS)
            wall_params['Length (mm)'] = str(length_mm)

            if not is_whole_number(length_mm):
                wall_params['ID'] = output.linkify(wall.Id)
                non_whole_walls_info.append(wall_params)
                override = DB.OverrideGraphicSettings()
                override.SetProjectionLineColor(DB.Color(255, 0, 0))
                override.SetCutLineColor(DB.Color(255, 0, 0))
                current_view.SetElementOverrides(wall.Id, override)

    t.Commit()

columns = sorted(list(set(param for wall_info in non_whole_walls_info for param in wall_info)))
table_data = []
for wall_info in non_whole_walls_info:
    row = [wall_info.get(column, '') for column in columns]
    table_data.append(row)

output.print_table(table_data=table_data,
                   title="Identified Walls",
                   columns=columns)
output.indeterminate_progress(False)
uidoc.RefreshActiveView()
