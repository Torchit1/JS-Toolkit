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
        tags = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(IndependentTag).ToElements()
        if not tags:
            print("No tags found.")
            return tag_data

        for tag in tags:
            tag_id = tag.Id.IntegerValue
            tagged_element_id = tag.TaggedLocalElementId.IntegerValue if hasattr(tag, 'TaggedLocalElementId') else 'No Tagged Element'

            tagged_element = doc.GetElement(tag.TaggedLocalElementId)
            tagged_element_name, tagged_element_category, tagged_element_type_id = 'Unknown', 'Unknown', 'Unknown'
            if tagged_element:
                tagged_element_name = safe_get_property(tagged_element, 'Name')
                tagged_element_category = safe_get_property(tagged_element.Category, 'Name') if tagged_element.Category else 'No Category'
                tagged_element_type_id = tagged_element.GetTypeId().IntegerValue if tagged_element.GetTypeId() else 'No Type ID'

            tag_head_position = format_xyz(tag.TagHeadPosition) if hasattr(tag, 'TagHeadPosition') else "No Position"
            tag_view_type = get_view_type(doc, tag.OwnerViewId)

            #print("Tag ID: {0}, Tagged Element ID: {1}, Tagged Element Name: {2}, Tagged Element Category: {3}, Tagged Element Type ID: {4}, Tag Head Position: {5}, View Type: {6}".format(
            #    tag_id, tagged_element_id, tagged_element_name, tagged_element_category, tagged_element_type_id, tag_head_position, tag_view_type))

            tag_data.append([tag_id, tagged_element_id, tagged_element_name, tagged_element_category, tagged_element_type_id, tag_head_position, tag_view_type])

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
