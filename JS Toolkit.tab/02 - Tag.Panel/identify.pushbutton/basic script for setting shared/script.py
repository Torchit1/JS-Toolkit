import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from Autodesk.Revit.DB import Transaction, StorageType
from System.Windows.Forms import Form, Label, TextBox, Button, DialogResult
from System.Drawing import Point

# Function to set a shared parameter value for an element type
def set_shared_parameter(element_type, param_name, value):
    param = element_type.LookupParameter(param_name)
    if param and param.StorageType == StorageType.Double:
        param.Set(value)

# Custom form for user input
class InputForm(Form):
    def __init__(self):
        self.Text = "Set Offsets"

        self.label1 = Label(Text="Vertical Offset:")
        self.label1.Location = Point(10, 10)
        self.label1.Width = 100
        self.Controls.Add(self.label1)

        self.textbox1 = TextBox()
        self.textbox1.Location = Point(120, 10)
        self.textbox1.Width = 100
        self.Controls.Add(self.textbox1)

        self.label2 = Label(Text="Horizontal Offset:")
        self.label2.Location = Point(10, 40)
        self.label2.Width = 100
        self.Controls.Add(self.label2)

        self.textbox2 = TextBox()
        self.textbox2.Location = Point(120, 40)
        self.textbox2.Width = 100
        self.Controls.Add(self.textbox2)

        self.button1 = Button(Text="Apply")
        self.button1.Location = Point(120, 70)
        self.button1.Click += self.button1_click
        self.Controls.Add(self.button1)

    def button1_click(self, sender, args):
        self.DialogResult = DialogResult.OK

# Main execution
if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument

    selected_ids = uidoc.Selection.GetElementIds()
    selected_elements = [doc.GetElement(id) for id in selected_ids]

    # Show input form and process input
    form = InputForm()
    dialogResult = form.ShowDialog()

    if dialogResult == DialogResult.OK:
        new_vertical_offset = float(form.textbox1.Text)
        new_horizontal_offset = float(form.textbox2.Text)

        transaction = Transaction(doc, "Update Shared Parameters")
        try:
            transaction.Start()
            for element in selected_elements:
                element_type = doc.GetElement(element.GetTypeId())
                set_shared_parameter(element_type, "VerticalOffset", new_vertical_offset)
                set_shared_parameter(element_type, "HorizontalOffset", new_horizontal_offset)
            transaction.Commit()
            print("Offsets updated.")
        except Exception as e:
            print("Error: " + str(e))
            if transaction.GetStatus() == TransactionStatus.Started:
                transaction.RollBack()

# Run the application form
