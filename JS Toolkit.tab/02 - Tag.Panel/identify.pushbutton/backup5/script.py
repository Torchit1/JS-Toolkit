import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import *
from pyrevit import script
from RevitServices.Transactions import TransactionManager
from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs

xamlfile = script.get_bundle_file('ui.xaml')


import wpf
from System import Windows

# Function to safely get an element's property
def safe_get_property(element, property_name):
    try:
        return getattr(element, property_name, 'Property Not Found or Accessible')
    except Exception as e:
        return 'Error Accessing Property: ' + str(e)

# Function to format XYZ coordinates
def format_xyz(xyz):
    return "X: {:.2f}, Y: {:.2f}, Z: {:.2f}".format(xyz.X, xyz.Y, xyz.Z) if xyz else "No Position"

# Function to get the view type from a view ID
def get_view_type(doc, view_id):
    view = doc.GetElement(view_id)
    return view.ViewType.ToString() if view else "Unknown View Type"

def set_shared_parameter(element, param_name, value):
    param = element.LookupParameter(param_name)
    if param:
        try:
            param.Set(value)
            print("Set {} to {} on element ID {}".format(param_name, value, element.Id.IntegerValue))
        except Exception as e:
            print("Failed to set {} to {} on element ID {}: {}".format(param_name, value, element.Id.IntegerValue, str(e)))
    else:
        print("Parameter {} not found on element ID {}".format(param_name, element.Id.IntegerValue))

def debug_parameters(element):
    try:
        print("\nElement ID: {}".format(element.Id.IntegerValue))
        params = element.Parameters
        for param in params:
            param_name = param.Definition.Name
            param_value = param.AsValueString() if param.HasValue else "No Value"
            print("  - Parameter: {}, Value: {}".format(param_name, param_value))
    except Exception as e:
        print("Error in debug_parameters: {}".format(str(e)))

# Function to update shared parameters based on tag data
def update_shared_parameters(doc, tag_data):
    """Update the shared parameters for each element based on tag data."""
    transaction = Transaction(doc, "Update Shared Parameters")
    transaction.Start()
    try:
        for item in tag_data:
            element_id = ElementId(item.TaggedElementID)
            element = doc.GetElement(element_id)
            if element:
                # Debugging: Print current values before updating
                print("Element ID: {}, Current HorizontalOffset: {}, New Value: {}".format(
                    element_id,
                    read_shared_parameter(element, "HorizontalOffset"),
                    item.HorizontalOffset
                ))
                print("Element ID: {}, Current VerticalOffset: {}, New Value: {}".format(
                    element_id,
                    read_shared_parameter(element, "VerticalOffset"),
                    item.VerticalOffset
                ))

                # Update the parameters
                set_shared_parameter(element, "HorizontalOffset", item.HorizontalOffset)
                set_shared_parameter(element, "VerticalOffset", item.VerticalOffset)

                # Debugging: Confirm update
                print("Updated Element ID: {}, New HorizontalOffset: {}, New VerticalOffset: {}".format(
                    element_id,
                    read_shared_parameter(element, "HorizontalOffset"),
                    read_shared_parameter(element, "VerticalOffset")
                ))
        transaction.Commit()
    except Exception as e:
        print("Error in transaction: {}".format(str(e)))
        transaction.RollBack()


# Main function to process elements and tags
def Main(doc):
    tag_data = []
    try:
        elements = FilteredElementCollector(doc, doc.ActiveView.Id).WhereElementIsNotElementType().ToElements()
        elements = [elem for elem in elements if not isinstance(elem, IndependentTag)]

        tags = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(IndependentTag).ToElements()
        tag_dict = {tag.TaggedLocalElementId.IntegerValue: tag for tag in tags}

        for elem in elements:
            element_id = elem.Id.IntegerValue
            element_name = safe_get_property(elem, 'Name')
            element_category = safe_get_property(elem.Category, 'Name') if elem.Category else 'No Category'
            element_type_id = elem.GetTypeId().IntegerValue if elem.GetTypeId() else 'No Type ID'
            element_family = 'Unknown'
            if hasattr(elem, 'Symbol') and elem.Symbol:
                element_family = safe_get_property(elem.Symbol.Family, 'Name')
            debug_parameters(elem)

            tag_id, tag_head_position, tag_view_type = 'Not Tagged', 'No Position', 'No View'
            element_type = doc.GetElement(elem.GetTypeId())
            horizontal_offset = 0
            vertical_offset = 0
            if element_type:
                horizontal_offset = read_shared_parameter(element_type, "HorizontalOffset")
                vertical_offset = read_shared_parameter(element_type, "VerticalOffset")

            if element_id in tag_dict:
                tag = tag_dict[element_id]
                tag_id = tag.Id.IntegerValue
                tag_head_position = format_xyz(tag.TagHeadPosition) if hasattr(tag, 'TagHeadPosition') else "No Position"
                tag_view_type = get_view_type(doc, tag.OwnerViewId)

            tag_data.append(TagDataItem(
                tag_id,                # Tag ID
                element_family,        # Tagged Element Family
                element_id,            # Tagged Element ID
                element_name,          # Tagged Element Name
                element_category,      # Tagged Element Category
                element_type_id,       # Tagged Element Type ID
                tag_head_position,     # Tag Head Position
                horizontal_offset,     # Horizontal Offset
                vertical_offset,       # Vertical Offset
                tag_view_type          # View Type
            ))

    except Exception as e:
        print("Error: {0}".format(str(e)))

    return tag_data
def read_shared_parameter(element_type, param_name):
    """Read the value of a shared parameter from an element type."""
    param = element_type.LookupParameter(param_name)
    if param:
        if param.StorageType == StorageType.Double:
            return param.AsDouble()
        elif param.StorageType == StorageType.Integer:
            return param.AsInteger()
        # Add additional handling for other storage types if necessary
    return 0

# Class to represent tag data items
class TagDataItem(INotifyPropertyChanged):
    def __init__(self, tag_id, tagged_element_family, tagged_element_id, tagged_element_name, tagged_element_category, tagged_element_type_id, tag_head_position, horizontal_offset, vertical_offset, view_type):
        self._tag_id = tag_id
        self._tagged_element_family = tagged_element_family
        self._tagged_element_id = tagged_element_id  # Make sure this is correctly assigned
        self._tagged_element_name = tagged_element_name
        self._tagged_element_category = tagged_element_category
        self._tagged_element_type_id = tagged_element_type_id
        self._tag_head_position = tag_head_position
        self._horizontal_offset = horizontal_offset
        self._vertical_offset = vertical_offset
        self._view_type = view_type
        self._property_changed_handlers = []

    @property
    def TagID(self):
        return self._tag_id

    @property
    def TaggedElementFamily(self):
        return self._tagged_element_family
    
    @property
    def TaggedElementID(self):
        return self._tagged_element_id

    @property
    def TaggedElementName(self):
        return self._tagged_element_name

    @property
    def TaggedElementCategory(self):
        return self._tagged_element_category

    @property
    def TaggedElementTypeID(self):
        return self._tagged_element_type_id

    @property
    def TagHeadPosition(self):
        return self._tag_head_position

    @property
    def ViewType(self):
        return self._view_type

    @property
    def HorizontalOffset(self):
        return self._horizontal_offset

    @HorizontalOffset.setter
    def HorizontalOffset(self, value):
        if self._horizontal_offset != value:
            self._horizontal_offset = value
            self.OnPropertyChanged("HorizontalOffset")

    @property
    def VerticalOffset(self):
        return self._vertical_offset

    @VerticalOffset.setter
    def VerticalOffset(self, value):
        if self._vertical_offset != value:
            self._vertical_offset = value
            self.OnPropertyChanged("VerticalOffset")

    def OnPropertyChanged(self, propertyName):
        for handler in self._property_changed_handlers:
            handler(self, PropertyChangedEventArgs(propertyName))

    def add_PropertyChanged(self, value):
        if value not in self._property_changed_handlers:
            self._property_changed_handlers.append(value)

    def remove_PropertyChanged(self, value):
        if value in self._property_changed_handlers:
            self._property_changed_handlers.remove(value)

# WPF window class
class MyWindow(Windows.Window):
    def __init__(self, tag_data):
        wpf.LoadComponent(self, xamlfile)
        self.listView = self.FindName("listview")
        self.applyButton = self.FindName("applyButton")
        self.applyButton.Click += self.on_apply_click

        for data in tag_data:
            self.listView.Items.Add(data)

        self.tag_data = tag_data

    def on_apply_click(self, sender, e):
        update_shared_parameters(__revit__.ActiveUIDocument.Document, self.tag_data)
        # Optionally, add a message to indicate successful update
        print("Parameters updated.")

# Entry point
if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    tag_data = Main(doc)
    window = MyWindow(tag_data)
    window.ShowDialog()