import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Retrieve a point family symbol to use for the model points
symbols = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()

# Print the names of up to 10 symbols
counter = 0
for symbol in symbols:
    try:
        print("Found symbol: " + symbol.Name + ", ElementId: " + str(symbol.Id))
    except:
        print("Skipping element due to error accessing Name property, ElementId: " + str(symbol.Id))
    
    counter += 1
    if counter >= 10:
        break
