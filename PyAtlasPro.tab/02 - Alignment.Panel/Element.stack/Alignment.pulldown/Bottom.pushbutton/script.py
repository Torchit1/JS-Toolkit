from element_alignment_utils import align_elements
from pyrevit import revit

doc = revit.doc
selection = revit.get_selection()

align_elements(doc, selection, "bottom")