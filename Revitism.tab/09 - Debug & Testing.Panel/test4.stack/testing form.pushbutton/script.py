import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('PresentationFramework')
clr.AddReference('System.Windows.Forms')

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ViewSheet, Transaction, BuiltInParameter
from System.Collections.ObjectModel import ObservableCollection
from System import Array
from System.Windows.Markup import XamlReader
from System.Windows import Window, Controls

class SheetInfo(object):
    def __init__(self, id, number, name, issue_date, created_by):
        self.Id = id
        self.Number = number
        self.Name = name
        self.IssueDate = issue_date
        self.CreatedBy = created_by

def get_sheet_infos(doc):
    sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    sheet_infos = []
    for sheet in sheets:
        issue_date = sheet.get_Parameter(BuiltInParameter.SHEET_ISSUE_DATE).AsString() or "N/A"
        created_by = sheet.get_Parameter(BuiltInParameter.SHEET_SCHEDULED).AsString() or "N/A"
        sheet_infos.append(SheetInfo(sheet.Id, sheet.SheetNumber, sheet.Name, issue_date, created_by))
    return Array[SheetInfo](sheet_infos)

def update_sheet_info(doc, updated_sheet_info):
    t = Transaction(doc, "Update Sheet Info")
    t.Start()
    try:
        for sheet_info in updated_sheet_info:
            sheet = doc.GetElement(sheet_info.Id)
            if sheet:
                sheet.Name = sheet_info.Name
                existing_sheet_numbers = [s.SheetNumber for s in FilteredElementCollector(doc).OfClass(ViewSheet) if s.Id != sheet.Id]
                if sheet_info.Number not in existing_sheet_numbers:
                    sheet.SheetNumber = sheet_info.Number
                else:
                    print("Conflict: Sheet number '{}' already exists.".format(sheet_info.Number))
        t.Commit()  # Commit changes
    except Exception as e:
        print("Error during update: " + str(e))
        t.RollBack()  # Roll back in case of errors

xaml_content = """
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Sheet Information" Height="300" Width="400">
    <StackPanel>
        <DataGrid x:Name="sheetsDataGrid" AutoGenerateColumns="False" Margin="10" CanUserAddRows="False">
            <DataGrid.Columns>
                <DataGridTextColumn Header="Sheet Number" Binding="{Binding Number, Mode=TwoWay}" Width="Auto" IsReadOnly="False"/>
                <DataGridTextColumn Header="Sheet Name" Binding="{Binding Name, Mode=TwoWay}" Width="Auto" IsReadOnly="False"/>
                <DataGridTextColumn Header="Issue Date" Binding="{Binding IssueDate}" Width="Auto" IsReadOnly="True"/>
                <DataGridTextColumn Header="Created By" Binding="{Binding CreatedBy}" Width="Auto" IsReadOnly="True"/>
            </DataGrid.Columns>
        </DataGrid>
        <Button x:Name="saveButton" Content="Save Changes" Margin="10" Height="30"/>
    </StackPanel>
</Window>
"""

window = XamlReader.Parse(xaml_content)
doc = __revit__.ActiveUIDocument.Document
sheet_data = ObservableCollection[SheetInfo](get_sheet_infos(doc))
window.FindName('sheetsDataGrid').ItemsSource = sheet_data

save_button = window.FindName('saveButton')
save_button.Click += lambda s, e: update_sheet_info(doc, sheet_data)

window.ShowDialog()
