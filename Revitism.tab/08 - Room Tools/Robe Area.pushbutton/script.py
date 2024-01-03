from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, Element, Transaction, OverrideGraphicSettings, Color)
from Autodesk.Revit.DB.Architecture import Room
from pyrevit import revit, DB, script
import pickle, json, os 
from pyrevit import forms

# Custom form to get default values
class DefaultValuesForm(forms.WPFWindow):
    def __init__(self, script_dir):
        xaml_file_path = os.path.join(script_dir, 'DefaultValuesForm.xaml')
        forms.WPFWindow.__init__(self, xaml_file_path)
        
        # Load default values from file
        with open(os.path.join(script_dir, 'default_values.json'), 'r') as file:
            self.default_values = json.load(file)
        
        self.set_default_values(self.default_values)
        self.cancelled = False  # Add this line to initialize the property

    def set_default_values(self, default_values):
        self.bed1_width_textbox.Text = str(default_values['Bed 1']['width'])
        self.bed1_depth_textbox.Text = str(default_values['Bed 1']['depth'])
        self.bed1_height_textbox.Text = str(default_values['Bed 1']['height'])
        self.other_width_textbox.Text = str(default_values['Other']['width'])
        self.other_depth_textbox.Text = str(default_values['Other']['depth'])
        self.other_height_textbox.Text = str(default_values['Other']['height'])
        self.epsilon_textbox.Text = str(default_values['epsilon'])
        self.verbose_checkbox.IsChecked = default_values['verbose_output']

    def on_save_click(self, sender, e):
        # Update default values
        self.default_values['Bed 1']['width'] = float(self.bed1_width_textbox.Text)
        self.default_values['Bed 1']['depth'] = float(self.bed1_depth_textbox.Text)
        self.default_values['Bed 1']['height'] = float(self.bed1_height_textbox.Text)
        self.default_values['Other']['width'] = float(self.other_width_textbox.Text)
        self.default_values['Other']['depth'] = float(self.other_depth_textbox.Text)
        self.default_values['Other']['height'] = float(self.other_height_textbox.Text)
        self.default_values['epsilon'] = float(self.epsilon_textbox.Text)
        self.default_values['verbose_output'] = self.verbose_checkbox.IsChecked
        
        # Save updated values to file
        with open(os.path.join(script_dir, 'default_values.json'), 'w') as file:
            json.dump(self.default_values, file, indent=4)
        
        self.Close()
        
    def on_cancel_click(self, sender, e):
        # Save updated values to file
        with open(os.path.join(script_dir, 'default_values.json'), 'w') as file:
            json.dump(self.default_values, file, indent=4)
        
        self.Close()
        
# Determine if Shift was held down while clicking the button
verbose_debug = __shiftclick__  # pyRevit sets this variable

# Get the logger and output
logger = script.get_logger()
output = script.get_output()

def get_solid_fill_pat(doc=revit.doc):
    fill_pats = DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement)
    solid_pat = [pat for pat in fill_pats if pat.GetFillPattern().IsSolidFill]
    return solid_pat[0]

output = script.get_output()
script_dir = os.path.dirname(__file__)




# Load or Show form to get default values
form = None  # Initialize form variable outside of if block
if __shiftclick__:
    # Show custom form
    form = DefaultValuesForm(script_dir)  # Pass script_dir as argument
    form.ShowDialog()
    # Retrieve entered values from the form
    default_values = form.default_values  # Updated to use form.default_values
else:
    # Load default values from file if not Shift+Click
    with open(os.path.join(script_dir, 'default_values.json'), 'r') as file:
        default_values = json.load(file)

verbose_debug = default_values['verbose_output']  # Use verbose setting from form


# Define robe criteria and epsilon from default values
robe_criteria = {
    'Bed 1': {
        'width': default_values['Bed 1']['width'],
        'depth': default_values['Bed 1']['depth'],
        'height': default_values['Bed 1']['height']
    },
    'Other': {
        'width': default_values['Other']['width'],
        'depth': default_values['Other']['depth'],
        'height': default_values['Other']['height']
    }
}
epsilon = default_values['epsilon']  # Tolerance for floating-point comparisons

# Exit the script if the Cancel button was clicked
if form and form.cancelled:  # Check if form is not None and if cancelled is True
    script.exit()  # Exit script early

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

if verbose_debug:
    output.print_md("# Code Explanation:")
    output.print_md("""
    This code checks each room with 'bed' in its name in the Revit document to see if it contains a robe, calculates the area of the robe, and checks if the robe meets the specified criteria based on the room name.
    """)
    output.print_md("\nStarting room check:")

rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
casework_elements = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Casework).WhereElementIsNotElementType().ToElements()


if not rooms:
    if verbose_debug:
        output.print_md("No rooms found in the document.")
else:
    if verbose_debug:
        output.print_md("Found {} rooms in the document.".format(len(rooms)))

room_data = {}
robe_criteria = {'Bed 1': default_values['Bed 1']['width'], 'Other': default_values['Other']['width']}  # Adjusted robe width criteria
min_rob_height = default_values['Bed 1']['height']  # Minimum robe height criteria in meters
min_rob_depth = default_values['Bed 1']['depth']   # Minimum robe depth criteria in meters
epsilon = default_values['epsilon']  # Tolerance for floating-point comparisons

EXCESSIVE_THRESHOLD = 100  # Define a constant for the excessive threshold

try:
    for room in rooms:
        if isinstance(room, Room):
            room_name = room.LookupParameter('Name').AsString()
            room_number = room.LookupParameter('Number').AsString()

            
            if "bed" in room_name.lower():
                robe_present = False
                robe_area = None
                robe_width = None
                robe_depth = None
                robe_height = None

                for element in casework_elements:
                    if "Robe" in Element.Name.GetValue(element):
                        location = element.Location.Point if element.Location else None
                        if location and room.IsPointInRoom(location):
                            robe_present = True
                            robe_width_param = element.LookupParameter('Width')
                            robe_depth_param = element.LookupParameter('Depth')
                            robe_height_param = element.LookupParameter('Height')
                            
                            if robe_width_param and robe_depth_param and robe_height_param:
                                robe_width = robe_width_param.AsDouble() * 0.3048
                                robe_depth = robe_depth_param.AsDouble() * 0.3048
                                robe_height = robe_height_param.AsDouble() * 0.3048
                                robe_area = robe_width * robe_depth
                            break
                
                meets_criteria = False
                if room_name.upper() == 'BED 1':  # Convert to uppercase for case-insensitive comparison
                    meets_criteria = (
                        robe_width >= robe_criteria['Bed 1'] - epsilon and 
                        robe_depth >= min_rob_depth - epsilon and 
                        robe_height >= min_rob_height - epsilon
                    )
                    
                else:
                    meets_criteria = (
                        robe_width >= robe_criteria['Other'] - epsilon and 
                        robe_depth >= min_rob_depth - epsilon and 
                        robe_height >= min_rob_height - epsilon
                    )
                    
               


                room_data[room.Id] = (room_name, room_number, robe_present, robe_area, robe_width, robe_depth, robe_height, meets_criteria)
                
                # Colorizing robes
                t = Transaction(doc, 'Colorize Robes')
                t.Start()
                try:
                    ogs = OverrideGraphicSettings()
                    if meets_criteria:
                        ogs.SetCutForegroundPatternColor(Color(0, 255, 0))
                    else:
                        ogs.SetCutForegroundPatternColor(Color(255, 0, 0))
                    ogs.SetCutForegroundPatternId(get_solid_fill_pat(doc).Id)
                    ogs.SetCutForegroundPatternVisible(True)
                    doc.ActiveView.SetElementOverrides(element.Id, ogs)
                    t.Commit()
                except Exception as e:
                    output.print_md("Error applying color: **{}**".format(e))
                    t.RollBack()

except Exception as e:
    output.print_md("Error: **{}**".format(e))

    
if verbose_debug:
    output.print_md("## Room Check Summary:")
    for id, (room_name, room_number, robe_present, robe_area, robe_width, robe_depth, robe_height, meets_criteria) in room_data.items():
        output.print_md("-------------------------------------")
        output.print_md('Room Name: **{}**'.format(room_name))
        output.print_md('Room Number: **{}**'.format(room_number))
        criteria_status = "Meets criteria" if meets_criteria else "Does not meet criteria"
        output.print_md(
            'Robe present with Area: **{:.2f} m2**, '
            'Width: **{:.2f} m**, Depth: **{:.2f} m**, Height: **{:.2f} m** - {}'.format(
                robe_area, robe_width, robe_depth, robe_height, criteria_status
            )
        )
        if meets_criteria:
            output.print_html('<p class="compliance-cell green-compliance">Meets criteria</p>')
        else:
            output.print_html('<p class="compliance-cell red-compliance">Does not meet criteria</p>')
    output.print_md("\n-------------------------------------")
    output.print_md("Room check completed.")

# Define the style for the compliance cell
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

