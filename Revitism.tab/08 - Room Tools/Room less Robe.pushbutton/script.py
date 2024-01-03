from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, Element)
from Autodesk.Revit.DB.Architecture import Room
from pyrevit import revit, DB, script

output = script.get_output()

style_code = """
.compliance-cell {
    padding: 8px;
    margin: 4px 0;
    border-radius: 4px;
}

.green-compliance {
    background-color: #e0ffe0; /* Light green background */
    color: green;
    font-size: 1.2em; /* Larger font size */
}

.red-compliance {
    background-color: #ffe0e0; /* Light red background */
    color: red;
    font-size: 1.2em; /* Larger font size */
}
"""

output.add_style(style_code)

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

output.print_md("# Code Explanation:")
output.print_md("""
This script conducts an analysis on rooms within a Revit document, specifically targeting rooms that include 'bed' in their names. The script is designed to validate these rooms against the specified area and robe (wardrobe) criteria, following the Australian Apartment Design Guidelines. 

### Formatting & Case Sensitivity:
- Room Names: The script identifies rooms by looking for the substring 'bed' in room names. This search is case-insensitive, so it will match 'Bed', 'bed', 'BED', etc. Ensure that the room names are appropriately formatted to be identified by the script.
- Parameters: The script retrieves parameters like 'Name', 'Number', 'Width', and 'Depth' from the Revit elements. These parameter names are case-sensitive, so they must be entered exactly as shown.

### Parameters:
- Room Area: The script calculates the room area and adjusts it based on the presence and dimensions of robes within each room. It then compares the adjusted area against predefined criteria for compliance.
- Robe Dimensions: Robe dimensions are extracted using 'Width' and 'Depth' parameters. Ensure these parameters are correctly assigned and populated in Revit for accurate calculations.

### Recommendations for Use:
- Before running the script, review and confirm that room names and parameters in the Revit document are set up correctly to prevent identification and calculation errors.
- For accurate compliance checking, update the `area_criteria` and `robe_criteria` dictionaries within the script to match the area and robe size standards you wish to enforce.
""")
output.print_md("\nStarting Room Analysis:")
output.print_md("""
The script is initiating the analysis of rooms with 'bed' in their names to verify compliance with the Australian Apartment Design Guidelines. It will measure and evaluate each room's area and robe dimensions against the specified criteria, providing a comprehensive review of living space design for optimal comfort and functionality.
""")


rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
casework_elements = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Casework).WhereElementIsNotElementType().ToElements()

room_data = {}
area_criteria = {'Bed 1': 10, 'Bed': 9}
robe_criteria = {'Bed 1': 1.8, 'Other': 1.5}
robe_Height_criteria = {'Bed 1': 2.1, 'Other': 2.1}

area_compliance_count = 0
robe_compliance_count = 0
total_compliance_count = 0
total_wasted_room_area = 0

try:
    for room in rooms:
        if isinstance(room, Room):
            room_name = room.LookupParameter('Name').AsString() if room.LookupParameter('Name') else None
            room_number = room.LookupParameter('Number').AsString() if room.LookupParameter('Number') else None
            
            if room_name and "bed" in room_name.lower():
                room_area = room.Area * 0.092903
                adjusted_room_area = room_area
                robe_present = False
                robe_area = 0
                robe_width = 0
                robe_height = 0 ##added height checking

                for element in casework_elements:
                    if "Robe" in Element.Name.GetValue(element):
                        location = element.Location.Point if element.Location else None
                        if location and room.IsPointInRoom(location):
                            robe_present = True
                            robe_width_param = element.LookupParameter('Width')
                            robe_depth_param = element.LookupParameter('Depth')
                            robe_height_param = element.LookupParameter('Height') ##added height checking
                            if robe_width_param and robe_depth_param and robe_height_param:
                                robe_width = robe_width_param.AsDouble() * 0.3048
                                robe_depth = robe_depth_param.AsDouble() * 0.3048
                                robe_height = robe_height_param.AsDouble() * 0.3048 ##added height checking
                                robe_area = robe_width * robe_depth
                                adjusted_room_area = room_area - robe_area
                            break
                
                area_meets_criteria = False
                robe_meets_criteria = False
                wasted_room_area = 0
                wasted_robe_width = 0
                for room_type, min_area in area_criteria.items():
                    if room_type.lower() in room_name.lower():
                        area_meets_criteria = adjusted_room_area >= min_area
                        wasted_room_area = adjusted_room_area - min_area
                
                if area_meets_criteria: area_compliance_count += 1
                if wasted_room_area > 0: total_wasted_room_area += wasted_room_area

                if room_name.upper() == 'BED 1':
                    robe_meets_criteria = robe_width >= robe_criteria['Bed 1']
                    wasted_robe_width = robe_width - robe_criteria['Bed 1']
                    robe_meets_Height_criteria = robe_height >= robe_Height_criteria['Bed 1']
                else:
                    robe_meets_criteria = robe_width >= robe_criteria['Other']
                    wasted_robe_width = robe_width - robe_criteria['Other']
                    robe_meets_Height_criteria = robe_height >= robe_Height_criteria['Other']

                if robe_meets_criteria: robe_compliance_count += 1
                if area_meets_criteria and robe_meets_criteria: total_compliance_count += 1

                room_data[room.Id] = (room_name, room_number, room_area, adjusted_room_area, area_meets_criteria, robe_present, robe_area, robe_width, robe_meets_criteria, robe_meets_Height_criteria, wasted_room_area, wasted_robe_width)
except Exception as e:
    output.print_md("Error: {}".format(e))

output.print_md("## Room Check Summary for Rooms with 'bed' in the Name:")
for id, data in room_data.items():
    room_name, room_number, original_area, area, area_meets_criteria, robe_present, robe_area, robe_width, robe_meets_criteria, robe_meets_Height_criteria, wasted_room_area, wasted_robe_width = data
    output.print_md("-------------------------------------")
    output.print_md('Room Name: **{}**'.format(room_name))
    output.print_md('Room Number: **{}**'.format(room_number))
    output.print_md('Original Room Area: **{:.2f} m2**'.format(float(original_area)))
    output.print_md('Robe present with Area: **{:.2f} m2**'.format(float(robe_area)))
    output.print_md('Robe Width: **{:.2f} m**'.format(float(robe_width)))
    output.print_md('Robe Height: **{:.2f} m**'.format(float(robe_height)))
    output.print_md('Room Area Less Robe: **{:.2f} m2**'.format(float(area)))
    output.print_md('Wasted Room Area: **{:.2f} m2**'.format(float(wasted_room_area)))
    output.print_md('Wasted Robe Width: **{:.2f} m**'.format(float(wasted_robe_width)))
    if area_meets_criteria:
        output.print_html('<p class="compliance-cell green-compliance">Area meets compliance</p>')
    else:
        output.print_html('<p class="compliance-cell red-compliance">Area does not meet compliance</p>')

    if robe_meets_criteria:
        output.print_html('<p class="compliance-cell green-compliance">Robe meets compliance</p>')
    else:
        output.print_html('<p class="compliance-cell red-compliance">Robe does not meet compliance</p>')
        
    if robe_meets_Height_criteria:
        output.print_html('<p class="compliance-cell green-compliance">Robe Height meets compliance</p>')
    else:
        output.print_html('<p class="compliance-cell red-compliance">Robe does not meet Height compliance</p>')

output.print_md("\n-------------------------------------")
output.print_md("Room check completed.")
output.print_md("=====================================")
output.print_md("Summary:")
output.print_md("Total Rooms Checked: **{}**".format(len(room_data)))
output.print_md("Total Wasted Room Area: **{:.2f} m2**".format(float(total_wasted_room_area)))
output.print_md("Rooms Meeting Area Compliance: **{}**".format(area_compliance_count))
output.print_md("Rooms Meeting Robe Compliance: **{}**".format(robe_compliance_count))
output.print_md("Rooms Meeting Both Compliances: **{}**".format(total_compliance_count))
output.print_md("=====================================")

