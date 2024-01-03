import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from Autodesk.Revit.DB import Transaction, Viewport, XYZ, FilteredElementCollector, BuiltInCategory, View, ViewType, FamilySymbol
from System.Windows.Forms import Application, Form, ListBox, Button, Label, TextBox, DialogResult, SelectionMode
from System.Drawing import Point, Size
from pyrevit import revit, DB

doc = revit.doc
# Custom Form
def get_title_block_types(doc):
        collector = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_TitleBlocks)
        return {tb.FamilyName + ": " + tb.Family.Name: tb for tb in collector}




class CustomForm(Form):
    def __init__(self, sheet_dict, view_dict, title_block_dict):
        self.sheet_dict = sheet_dict
        self.view_dict = view_dict
        self.title_block_dict = title_block_dict
        self.Text = 'Place or Remove Views on Sheet'
        self.Size = Size(750, 400)

        self.init_ui()

    def init_ui(self):



        label1 = Label()
        label1.Text = 'Select Sheet:'
        label1.Size = Size(100, 20)
        label1.Location = Point(20, 20)
        self.Controls.Add(label1)

        self.sheet_list = ListBox()
        self.sheet_list.Size = Size(300, 120)
        for sheet in sorted(self.sheet_dict.keys()):
            self.sheet_list.Items.Add(sheet)
        self.sheet_list.Location = Point(20, 50)
        self.Controls.Add(self.sheet_list)

        label2 = Label()
        label2.Text = 'Select Views:'
        label2.Size = Size(100, 20)
        label2.Location = Point(400, 20)
        self.Controls.Add(label2)

        self.view_list = ListBox()
        self.view_list.Size = Size(300, 120)
        for view in sorted(self.view_dict.keys()):
            self.view_list.Items.Add(view)
        self.view_list.Location = Point(400, 50)
        self.view_list.SelectionMode = SelectionMode.MultiExtended
        self.Controls.Add(self.view_list)

        label3 = Label()
        label3.Text = 'Rows:'
        label3.Size = Size(50, 20)
        label3.Location = Point(20, 180)
        self.Controls.Add(label3)

        self.row_textbox = TextBox()
        self.row_textbox.Size = Size(50, 20)
        self.row_textbox.Location = Point(80, 180)
        self.Controls.Add(self.row_textbox)

        label4 = Label()
        label4.Text = 'Columns:'
        label4.Size = Size(70, 20)
        label4.Location = Point(140, 180)
        self.Controls.Add(label4)

        self.column_textbox = TextBox()
        self.column_textbox.Size = Size(50, 20)
        self.column_textbox.Location = Point(220, 180)
        self.Controls.Add(self.column_textbox)

        label5 = Label()
        label5.Text = 'Row Spacing (mm):'
        label5.Size = Size(120, 20)
        label5.Location = Point(20, 210)
        self.Controls.Add(label5)

        self.row_spacing_textbox = TextBox()
        self.row_spacing_textbox.Size = Size(50, 20)
        self.row_spacing_textbox.Location = Point(150, 210)
        self.Controls.Add(self.row_spacing_textbox)

        label6 = Label()
        label6.Text = 'Column Spacing (mm):'
        label6.Size = Size(140, 20)
        label6.Location = Point(210, 210)
        self.Controls.Add(label6)

        self.column_spacing_textbox = TextBox()
        self.column_spacing_textbox.Size = Size(50, 20)
        self.column_spacing_textbox.Location = Point(360, 210)
        self.Controls.Add(self.column_spacing_textbox)

        # Adding Place Views button
        self.place_button = Button()
        self.place_button.Text = 'Place Views'
        self.place_button.Size = Size(100, 30)
        self.place_button.Location = Point(20, 250)
        self.place_button.Click += self.place_views
        self.Controls.Add(self.place_button)

        # Adding Remove Views button
        self.remove_button = Button()
        self.remove_button.Text = 'Remove Views'
        self.remove_button.Size = Size(100, 30)
        self.remove_button.Location = Point(140, 250)
        self.remove_button.Click += self.remove_views
        self.Controls.Add(self.remove_button)

        # Add ComboBox for title block selection
        self.title_block_list = ComboBox()
        self.title_block_list.Location = Point(400, 250)
        self.title_block_list.Size = Size(300, 21)
        for title_block in sorted(self.title_block_dict.keys()):
            self.title_block_list.Items.Add(title_block)
        self.Controls.Add(self.title_block_list)








    # Access the parameters for width and height
        width_param = selected_title_block.get_Parameter(BuiltInParameter.SYMBOL_WIDTH_PARAM)
        height_param = selected_title_block.get_Parameter(BuiltInParameter.SYMBOL_HEIGHT_PARAM)

        width = width_param.AsDouble()  # Convert from internal units if necessary
        height = height_param.AsDouble()  # Convert from internal units if necessary


    def place_views(self, sender, event):
        selected_sheet_name = self.sheet_list.SelectedItem
        selected_view_names = [self.view_list.Items[i] for i in self.view_list.SelectedIndices]
        num_rows = int(self.row_textbox.Text)
        num_columns = int(self.column_textbox.Text)

        row_spacing_mm = float(self.row_spacing_textbox.Text)
        column_spacing_mm = float(self.column_spacing_textbox.Text)
        row_spacing_ft = row_spacing_mm / 304.8  # Convert mm to feet
        column_spacing_ft = column_spacing_mm / 304.8  # Convert mm to feet

        selected_sheet = self.sheet_dict[selected_sheet_name]
        start_point = XYZ(0, 0, 0)
        x_spacing = column_spacing_ft
        y_spacing = row_spacing_ft

        with Transaction(doc, 'Place Views on Sheet') as t:
            t.Start()
            for idx, view_name in enumerate(selected_view_names):
                view = self.view_dict[view_name]
                row = idx // num_columns
                column = idx % num_columns
                x_offset = column * x_spacing
                y_offset = -row * y_spacing
                new_center = XYZ(start_point.X + x_offset, start_point.Y + y_offset, 0)
                Viewport.Create(doc, selected_sheet.Id, view.Id, new_center)
            t.Commit()
        self.DialogResult = DialogResult.OK


        selected_title_block_name = self.title_block_list.SelectedItem
        selected_title_block = self.title_block_dict[selected_title_block_name]

    def remove_views(self, sender, event):
        selected_sheet_name = self.sheet_list.SelectedItem
        selected_sheet = self.sheet_dict[selected_sheet_name]

        with Transaction(doc, 'Remove Views from Sheet') as t:
            t.Start()
            viewports_on_sheet = FilteredElementCollector(doc, selected_sheet.Id).OfClass(Viewport).ToElements()
            for vp in viewports_on_sheet:
                doc.Delete(vp.Id)
            t.Commit()
        self.DialogResult = DialogResult.OK

# Get all sheets in the document


title_block_types = get_title_block_types(doc)
title_block_dict = {"{} - {}".format(tb.Name, tb.FamilyName): tb for tb in title_block_types}

all_sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
sheet_dict = {"{} - {}".format(sheet.SheetNumber, sheet.Name): sheet for sheet in all_sheets}






# Get all views in the document
views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()

# Filter out views that are already placed on sheets and Drawing Sheet views
views_on_sheets = {vp.ViewId.IntegerValue for vp in FilteredElementCollector(doc).OfClass(Viewport).WhereElementIsNotElementType()}
filtered_views = {view for view in views if view.Id not in views_on_sheets and view.ViewType != ViewType.DrawingSheet}
view_dict = {
    "{} - {} - {}".format(view.ViewType.ToString(), view.Name, view.Id): view for view in filtered_views if not view.IsTemplate and view.CanBePrinted
}

# Run the form
Application.Run(CustomForm(sheet_dict, view_dict, title_block_dict))
