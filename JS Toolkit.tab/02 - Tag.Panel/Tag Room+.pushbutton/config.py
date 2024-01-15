from pyrevit import script, revit, DB
import pyrevit.forms as forms

my_config = script.get_config()

# Define frequently selected categories
FREQUENTLY_SELECTED_CATEGORIES = [
    DB.BuiltInCategory.OST_Doors,
    DB.BuiltInCategory.OST_Floors,
    DB.BuiltInCategory.OST_Walls,
    DB.BuiltInCategory.OST_Windows,
]

# Default toggle settings
DEFAULT_TOGGLE_SETTINGS = {
    'check_blank_tag': False,
    'toggle_tagged': True,
    'toggle_visibility': True,
    'tag_windows_in_plan': False
}

# Define toggleable settings
TOGGLE_SETTINGS = {
    'check_blank_tag': 'Remove Empty Tags',
    'toggle_tagged': 'Ignore Already Tagged Elements',
    'toggle_visibility': 'Tag Only if Visible in Current View',
    'tag_windows_in_plan': 'Special Tagging for Windows in Plan Views'
}


class FSCategoryItem(forms.TemplateListItem):
    """Wrapper class for frequently selected category list item"""
    pass


def get_taggable_categories():
    """Retrieve a list of taggable category names."""
    doc = revit.doc
    categories = doc.Settings.Categories
    taggable_categories = [cat.Name for cat in categories if cat.AllowsBoundParameters]
    return sorted(taggable_categories)


def load_configs():
    """Loads the configuration for selected categories."""
    selection_config = my_config.get_option('selection_config', [])
    return selection_config


def save_configs(selection_items):
    """Saves the configuration for selected categories."""
    my_config.selection_config = [x for x in selection_items]
    script.save_config()


def reset_defaults(options):
    """Reset frequently selected categories to defaults"""
    defaults = [revit.query.get_category(x).Name for x in FREQUENTLY_SELECTED_CATEGORIES]
    for opt in options:
        opt.checked = opt.name in defaults


def load_toggle_settings():
    """Load saved toggle settings or return defaults if not set."""
    saved_settings = my_config.get_option('toggle_settings', DEFAULT_TOGGLE_SETTINGS)
    return {key: saved_settings.get(key, DEFAULT_TOGGLE_SETTINGS[key]) for key in TOGGLE_SETTINGS}


def save_toggle_settings(settings):
    """Save the toggle settings."""
    my_config.toggle_settings = settings
    script.save_config()


def reset_toggle_settings(options):
    """Reset toggle settings to default values."""
    for opt in options:
        # Match the display name back to the key
        key = next(k for k, v in TOGGLE_SETTINGS.items() if v == opt.name)
        opt.checked = DEFAULT_TOGGLE_SETTINGS[key]


def toggle_settings_menu():
    """Displays a menu for additional toggle settings."""
    current_settings = load_toggle_settings()
    toggle_options = [FSCategoryItem(TOGGLE_SETTINGS[key], checked=current_settings[key]) for key in TOGGLE_SETTINGS]

    settings = forms.SelectFromList.show(
        toggle_options,
        title='Toggle Additional Settings',
        button_name='Save',
        multiselect=True,
        resetfunc=reset_toggle_settings  # Use the reset function
    )

    if settings is not None:
        new_settings = {key: (TOGGLE_SETTINGS[key] in settings) for key in TOGGLE_SETTINGS}
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


if __name__ == "__main__":
    config_menu()
