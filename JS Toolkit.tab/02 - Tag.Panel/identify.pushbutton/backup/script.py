import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag, XYZ, View

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

# Main method to execute script
def Main(doc):
    try:
        # Retrieve only tag elements in the active view
        tags = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(IndependentTag).ToElements()

        # Check if tag list is empty
        if not tags:
            print("No tags found.")
            return

        # Iterate through the tag elements and print their details
        for tag in tags:
            tag_id = tag.Id.IntegerValue
            tagged_element_id = tag.TaggedLocalElementId.IntegerValue if hasattr(tag, 'TaggedLocalElementId') else 'No Tagged Element'

            # Get the tagged element
            tagged_element = doc.GetElement(tag.TaggedLocalElementId)
            if tagged_element:
                tagged_element_name = safe_get_property(tagged_element, 'Name')
                tagged_element_category = safe_get_property(tagged_element.Category, 'Name') if tagged_element.Category else 'No Category'
                tagged_element_type_id = tagged_element.GetTypeId().IntegerValue if tagged_element.GetTypeId() else 'No Type ID'
            else:
                tagged_element_name = 'Tagged Element Not Found'
                tagged_element_category = 'Unknown'
                tagged_element_type_id = 'Unknown'

            # Get the position of the tag head
            tag_head_position = format_xyz(tag.TagHeadPosition) if hasattr(tag, 'TagHeadPosition') else "No Position"

            # Get the view type of the tag
            tag_view_type = get_view_type(doc, tag.OwnerViewId)

            #print("Tag ID: {0}, Tagged Element ID: {1}, Tagged Element Name: {2}, Tagged Element Category: {3}, Tagged Element Type ID: {4}, Tag Head Position: {5}, View Type: {6}".format(
            #    tag_id, tagged_element_id, tagged_element_name, tagged_element_category, tagged_element_type_id, tag_head_position, tag_view_type))

    except Exception as e:
        # In case of any errors, print the exception message
        print("Error: {0}".format(str(e)))

# Entry point for the script
if __name__ == "__main__":
    # Get the active document from the script context
    doc = __revit__.ActiveUIDocument.Document

    # Execute the main method
    Main(doc)
