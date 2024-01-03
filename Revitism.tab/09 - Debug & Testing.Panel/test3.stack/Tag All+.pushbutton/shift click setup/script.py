from pyrevit import EXEC_PARAMS
import config

def main():
    if EXEC_PARAMS.config_mode:
        print("Shift-Click Mode is ON")
        # Your shift-click logic goes here, such as opening a configuration menu
        config.config_menu()
    else:
        print("Normal Click Mode")
        # Your normal click logic goes here
        source_selection = config.load_configs()
        if source_selection:
            for item in source_selection:
                print(item)

if __name__ == "__main__":
    main()
