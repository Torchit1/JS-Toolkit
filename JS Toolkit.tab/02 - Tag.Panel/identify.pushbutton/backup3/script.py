import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag, XYZ, View
from pyrevit import script
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

def Main(doc):
    tag_data = []
    try:
        # Retrieve all elements in the active view
        elements = FilteredElementCollector(doc, doc.ActiveView.Id).WhereElementIsNotElementType().ToElements()

        # Retrieve all tags in the active view
        tags = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(IndependentTag).ToElements()
        tag_dict = {tag.TaggedLocalElementId.IntegerValue: tag for tag in tags}

        # Iterate through all elements to check if they are tagged
        for elem in elements:
            element_id = elem.Id.IntegerValue
            element_name = safe_get_property(elem, 'Name')
            element_category = safe_get_property(elem.Category, 'Name') if elem.Category else 'No Category'
            element_type_id = elem.GetTypeId().IntegerValue if elem.GetTypeId() else 'No Type ID'

            # Initialize tag-related properties as 'Not Tagged'
            tag_id, tag_head_position, tag_view_type = 'Not Tagged', 'No Position', 'No View'

            # Check if this element has a tag
            if element_id in tag_dict:
                tag = tag_dict[element_id]
                tag_id = tag.Id.IntegerValue
                tag_head_position = format_xyz(tag.TagHeadPosition) if hasattr(tag, 'TagHeadPosition') else "No Position"
                tag_view_type = get_view_type(doc, tag.OwnerViewId)

            tag_data.append([tag_id, element_id, element_name, element_category, element_type_id, tag_head_position, tag_view_type])

    except Exception as e:
        print("Error: {0}".format(str(e)))

    return tag_data


class TagDataItem(object):
    def __init__(self, tag_id, tagged_element_id, tagged_element_name, tagged_element_category, tagged_element_type_id, tag_head_position, view_type):
        self.TagID = tag_id
        self.TaggedElementID = tagged_element_id
        self.TaggedElementName = tagged_element_name
        self.TaggedElementCategory = tagged_element_category
        self.TaggedElementTypeID = tagged_element_type_id
        self.TagHeadPosition = tag_head_position
        self.ViewType = view_type

class MyWindow(Windows.Window):
    def __init__(self, tag_data):
        wpf.LoadComponent(self, xamlfile)
        self.listView = self.FindName("listview")

        for data in tag_data:
            item = TagDataItem(*data)
            self.listView.Items.Add(item)

if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    tag_data = Main(doc)
    window = MyWindow(tag_data)
    window.ShowDialog()
