import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag, XYZ, View, Transaction

# Function to move specific tags
def move_specific_tags(doc, target_family_type_id, offset_x):
    # Convert mm to feet (1 mm = 0.00328084 feet)
    offset_x_feet = offset_x * 0.00328084

    with Transaction(doc, "Move Specific Tags") as trans:
        trans.Start()
        tags = FilteredElementCollector(doc).OfClass(IndependentTag).ToElements()
        for tag in tags:
            tagged_element_id = tag.TaggedLocalElementId
            tagged_element = doc.GetElement(tagged_element_id)
            if tagged_element and tagged_element.GetTypeId().IntegerValue == target_family_type_id:
                if hasattr(tag, 'TagHeadPosition') and tag.TagHeadPosition:
                    current_pos = tag.TagHeadPosition
                    new_pos = XYZ(current_pos.X + offset_x_feet, current_pos.Y, current_pos.Z)
                    tag.TagHeadPosition = new_pos
        trans.Commit()

# Main method to execute script
def Main(doc):
    try:
        target_family_type_id = 421652  # Family type ID to target
        move_specific_tags(doc, target_family_type_id, 300)  # Move tags 300mm to the right

    except Exception as e:
        print("Error: {0}".format(str(e)))

# Entry point for the script
if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    Main(doc)
