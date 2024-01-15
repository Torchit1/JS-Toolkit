import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag, XYZ, View, Transaction, StorageType
from pyrevit import script
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from System import Windows

xamlfile = script.get_bundle_file('ui.xaml')
import wpf

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

# Function to read a shared parameter value from an element type
def read_shared_parameter(element_type, param_name):
    param = element_type.LookupParameter(param_name)
    if param:
        if param.StorageType == StorageType.Double:
            return param.AsDouble()
        elif param.StorageType == StorageType.Integer:
            return param.AsInteger()
    return 0

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

            tag_id, tag_head_position, tag_view_type = 'Not Tagged', 'No Position', 'No View'
            if element_id in tag_dict:
                tag = tag_dict[element_id]
                tag_id = tag.Id.IntegerValue
                tag_head_position = format_xyz(tag.TagHeadPosition) if hasattr(tag, 'TagHeadPosition') else "No Position"
                tag_view_type = get_view_type(doc, tag.OwnerViewId)

            # Read shared parameters
            element_type = doc.GetElement(elem.GetTypeId())
            horizontal_offset = read_shared_parameter(element_type, "HorizontalOffset")
            vertical_offset = read_shared_parameter(element_type, "VerticalOffset")

            tag_data.append([
                tag_id,                # Tag ID
                element_family,        # Tagged Element Family
                element_id,            # Tagged Element ID
                element_name,          # Tagged Element Name
                element_category,      # Tagged Element Category
                element_type_id,       # Tagged Element Type ID
                tag_head_position,     # Tag Head Position
                tag_view_type,         # View Type
                horizontal_offset,     # Horizontal Offset
                vertical_offset        # Vertical Offset
            ])

    except Exception as e:
        print("Error: {0}".format(str(e)))

    return tag_data

class TagDataItem(object):
    def __init__(self, tag_id, tagged_element_family, tagged_element_id, tagged_element_name, tagged_element_category, tagged_element_type_id, tag_head_position, view_type, horizontal_offset, vertical_offset):
        self.TagID = tag_id
        self.TaggedElementFamily = tagged_element_family
        self.TaggedElementID = tagged_element_id
        self.TaggedElementName = tagged_element_name
        self.TaggedElementCategory = tagged_element_category
        self.TaggedElementTypeID = tagged_element_type_id
        self.TagHeadPosition = tag_head_position
        self.ViewType = view_type
        self.HorizontalOffset = horizontal_offset
        self.VerticalOffset = vertical_offset

class MyWindow(Windows.Window):
    def __init__(self, tag_data):
        wpf.LoadComponent(self, xamlfile)
        self.listView = self.FindName("listview")
        self.ApplyButton = self.FindName("ApplyButton")

        if self.ApplyButton is not None:
            self.ApplyButton.Click += self.apply_button_click
        else:
            raise Exception("ApplyButton not found in XAML file.")

        for data in tag_data:
            item = TagDataItem(*data)
            self.listView.Items.Add(item)


    def apply_button_click(self, sender, e):
        doc = DocumentManager.Instance.CurrentDBDocument
        selected_items = self.listView.SelectedItems
        selected_elements = [doc.GetElement(item.TaggedElementID) for item in selected_items]

        vertical_offset = float(self.FindName("VerticalOffsetTextBox").Text)
        horizontal_offset = float(self.FindName("HorizontalOffsetTextBox").Text)

        TransactionManager.Instance.EnsureInTransaction(doc)
        try:
            for element in selected_elements:
                element_type = doc.GetElement(element.GetTypeId())
                set_shared_parameter(element_type, "VerticalOffset", vertical_offset)
                set_shared_parameter(element_type, "HorizontalOffset", horizontal_offset)
            TransactionManager.Instance.TransactionTaskDone()
            Windows.MessageBox.Show("Offsets updated successfully.", "Info")
        except Exception as ex:
            TransactionManager.Instance.ForceRollBack()
            Windows.MessageBox.Show("Error: " + str(ex), "Error")

if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    tag_data = Main(doc)
    window = MyWindow(tag_data)
    window.ShowDialog()