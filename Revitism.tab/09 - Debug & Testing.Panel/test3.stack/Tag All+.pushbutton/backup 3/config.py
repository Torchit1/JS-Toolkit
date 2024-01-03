from pyrevit import script, revit, DB

# Check if the forms module is available
try:
    import pyrevit.forms as forms
except ImportError:
    forms = script.forms

my_config = script.get_config()

FREQUENTLY_SELECTED_CATEGORIES = [
    DB.BuiltInCategory.OST_AreaSchemeLines,
    DB.BuiltInCategory.OST_Columns,
    DB.BuiltInCategory.OST_StructuralColumns,
    DB.BuiltInCategory.OST_Doors,
    DB.BuiltInCategory.OST_Floors,
    DB.BuiltInCategory.OST_StructuralFraming,
    DB.BuiltInCategory.OST_Walls,
    DB.BuiltInCategory.OST_Windows,
]



class FSCategoryItem(forms.TemplateListItem):
    """Wrapper class for frequently selected category list item"""
    pass
    
def get_taggable_categories():
    """Retrieve a list of taggable category names."""
    doc = revit.doc
    categories = doc.Settings.Categories
    taggable_categories = [cat.Name for cat in categories if cat.AllowsBoundParameters]
    return sorted(taggable_categories)

def is_shift_click_mode():
    """Checks if the current mode is shift-click."""
    return my_config.get_option('shift_click_mode', False)
    
def save_configs(selection_items):
    """Saves the configuration for selected categories."""
    my_config.selection_config = [x for x in selection_items]
    script.save_config()
    
def load_configs():
    """Loads the configuration for selected categories."""
    selection_config = my_config.get_option('selection_config', [])
    return selection_config
    
    
def reset_defaults(options):
    """Reset frequently selected categories to defaults"""
    defaults = [revit.query.get_category(x)
                for x in FREQUENTLY_SELECTED_CATEGORIES]
    default_names = [x.Name for x in defaults if x]
    for opt in options:
        if opt.name in default_names:
            opt.checked = True

# Define toggleable settings
TOGGLE_SETTINGS = {
    'check_blank_tag': 'Check Blank Tag',
    'toggle_tagged': 'Toggle Already Tagged',
    'toggle_visibility': 'Toggle Element Visibility'
}

def load_toggle_settings():
    """Load saved toggle settings."""
    return my_config.get_option('toggle_settings', {key: False for key in TOGGLE_SETTINGS})

def save_toggle_settings(settings):
    """Save the toggle settings."""
    my_config.toggle_settings = settings
    script.save_config()

def toggle_settings_menu():
    """Displays a menu for additional toggle settings."""
    current_settings = load_toggle_settings()
    toggle_options = [FSCategoryItem(key, checked=current_settings[key]) for key in TOGGLE_SETTINGS]
    settings = forms.SelectFromList.show(
        toggle_options,
        title='Toggle Additional Settings',
        button_name='Save',
        multiselect=True
    )

    if settings is not None:
        # Update settings based on user selection
        new_settings = {key: (key in settings) for key in TOGGLE_SETTINGS}
        save_toggle_settings(new_settings)

def config_menu():
    """Displays the configuration menu for category selection and toggle settings."""
    prev_config = load_configs()
    taggable_categories = get_taggable_categories()
    selection_config = forms.SelectFromList.show(
        [FSCategoryItem(x, checked=x in prev_config) for x in taggable_categories],
        title='Select Taggable Categories',
        button_name='Save',
        multiselect=True,
        resetfunc=reset_defaults
    )

    if selection_config:
        save_configs(selection_config)
        toggle_settings_menu()  # Call the second form for toggle settings

    return selection_config

if __name__ == "__main__":
    config_menu()