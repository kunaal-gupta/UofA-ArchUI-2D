import tkinter as tk
from tkinter import filedialog
import MapDesign
import os

def get_campus_and_building():
    root = tk.Tk()
    root.withdraw()
    building_folder = filedialog.askdirectory(
        title="Select Building Folder"
    )

    if not building_folder:
        print("No folder selected.")
        return None, None
    building_name = os.path.basename(building_folder).title()
    campus_name = os.path.basename(os.path.dirname(building_folder)).title()

    return campus_name, building_name

if __name__ == '__main__':
    campus, building = get_campus_and_building()
    print(f'Fetching {building} data from {campus} campus...')


    if campus and building:
        print("Building User interface.....")

        app = MapDesign.Application(building, campus)
        app.mainloop()
    else:
        print("Application exited without selecting a folder.")
