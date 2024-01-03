import sys
from pyrevit import revit, DB, script

logger = script.get_logger()

class ViewPortType:
    def __init__(self, rvt_element_type):
        self._rvt_type = rvt_element_type

    def __str__(self):
        return revit.query.get_name(self._rvt_type)

    @property
    def name(self):
        return str(self)

# Collect viewport types
all_element_types = \
    DB.FilteredElementCollector(revit.doc)\
      .OfClass(DB.ElementType)\
      .ToElements()

all_viewport_types = \
    [ViewPortType(x) for x in all_element_types if x.FamilyName == 'Viewport']

logger.debug('Viewport types: {}'.format(all_viewport_types))

# Print the names of the viewport types
print("Available viewport types:")
for viewport_type in all_viewport_types:
    print(viewport_type.name)




