# Import Python standard libraries
import os
import subprocess

# Import Revit API
from Autodesk.Revit.DB import Document, ModelPathUtils

# Import PyRevit
from pyrevit import revit, DB

# Get the current document (project)
doc = revit.doc  # type: Document

# Check if the document is saved. If it's not saved, it doesn't have a directory
if doc.IsWorkshared:
    model_path = doc.GetWorksharingCentralModelPath()
    folder_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(model_path)
else:
    folder_path = doc.PathName

# Check if folder_path is empty (unsaved document)
if not folder_path:
    print("Document is not saved. Save the document and try again.")
else:
    # Extract directory from full file path
    directory = os.path.dirname(folder_path)

    # Open the folder using the default file explorer
    subprocess.Popen('explorer "{}"'.format(directory))
