from pyrevit import script

# Check if the forms module is available
try:
    import pyrevit.forms as forms
except ImportError:
    forms = script.forms

my_config = script.get_config()

class FSCategoryItem(forms.TemplateListItem):
    """Wrapper class for frequently selected category list item"""
    pass

def load_configs():
    """Loads the configuration for selected categories."""
    selection_config = my_config.get_option('selection_config', [])
    return selection_config

def save_configs(selection_items):
    """Saves the configuration for selected categories."""
    my_config.selection_config = [x for x in selection_items]
    script.save_config()

def config_menu():
    """Displays the configuration menu for category selection."""
    prev_config = load_configs()
    item_list = ["item 1", "item 2"]
    selection_config = forms.SelectFromList.show(
        [FSCategoryItem(x, checked=x in prev_config) for x in item_list],
        title='Select Categories',
        button_name='Save',
        multiselect=True
    )

    if selection_config:
        # Directly save the selection_config list if it's a list of strings
        save_configs(selection_config)
    return selection_config

def toggle_click_mode():
    """Toggles the click mode between normal click and shift-click."""
    click_mode = my_config.get_option('shift_click_mode', False)
    my_config.shift_click_mode = not click_mode
    script.save_config()

def is_shift_click_mode():
    """Checks if the current mode is shift-click."""
    return my_config.get_option('shift_click_mode', False)

if __name__ == "__main__":
    config_menu()
