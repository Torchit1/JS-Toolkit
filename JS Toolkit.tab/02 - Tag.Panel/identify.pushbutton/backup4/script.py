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

            tag_data.append([
                tag_id,                # Tag ID
                element_family,        # Tagged Element Family
                element_id,            # Tagged Element ID
                element_name,          # Tagged Element Name
                element_category,      # Tagged Element Category
                element_type_id,       # Tagged Element Type ID
                tag_head_position,     # Tag Head Position
                tag_view_type          # View Type
            ])

    except Exception as e:
        print("Error: {0}".format(str(e)))

    return tag_data


class TagDataItem(object):
    def __init__(self, tag_id, tagged_element_family, tagged_element_id, tagged_element_name, tagged_element_category, tagged_element_type_id, tag_head_position, view_type):
        self.TagID = tag_id
        self.TaggedElementFamily = tagged_element_family
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
