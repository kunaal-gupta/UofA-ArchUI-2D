import os
import shutil
import tkinter as tk
import tkinter.messagebox as messagebox
import xml.etree.ElementTree as ET
from tkinter import simpledialog
from tkinter import ttk
from XMLDataExtract import directory_path, countLevels, LevelName
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BuildingMap = {}
BuildingName = directory_path.split('/')[-1]

def create_new_xml_folder(building_map, floor):
    # Define the project directory
    project_directory = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
    backup_folder_path = os.path.join(project_directory, "new_xml")

    # Create the backup folder if it doesn't exist
    if not os.path.exists(backup_folder_path):
        os.makedirs(backup_folder_path)
        print(f"New XML Directory created: {backup_folder_path}")

    # Define categories
    categories = [
        'Room',
        'Entrance',
        'Elevator',
        'Hallway',
        'Washroom',
        'StairPoints',
        'X'
    ]

    # Create level folder for the specified floor
    level_folder_path = os.path.join(backup_folder_path, f"Level_{floor}")

    # Check if the level folder already exists
    if os.path.exists(level_folder_path):
        print(f"Level folder {level_folder_path} already exists. Aborting operation.")
        return  # Exit the function if the level folder exists

    os.makedirs(level_folder_path, exist_ok=True)

    # Create subfolders for each category if they don't exist
    for category in categories:
        category_folder_path = os.path.join(level_folder_path, category)
        os.makedirs(category_folder_path, exist_ok=True)

    # Copy each XML file from BuildingMap to the backup folder
    for room_number, xml_paths in building_map.items():
        for xml_path in xml_paths:  # Iterate through the list of XML paths
            if os.path.exists(xml_path):
                # Logic to assign the XML file to a specific category
                if 'Entrance' in room_number:
                    category = 'Entrance'
                elif 'Elevator' in room_number:
                    category = 'Elevator'
                elif 'Hallway' in room_number:
                    category = 'Hallway'
                elif 'Washroom' in room_number:
                    category = 'Washroom'
                elif 'Stair' in room_number:
                    category = 'StairPoints'
                elif 'X' in room_number:
                    category = 'X'
                else:
                    category = 'Room'  # Default category

                # Construct the new file path in the appropriate category folder
                base_filename = f"{room_number}.xml"
                backup_file_path = os.path.join(level_folder_path, category, base_filename)

                # Check if file already exists and rename if necessary
                if os.path.exists(backup_file_path):
                    # Generate a new filename with a suffix
                    base, ext = os.path.splitext(base_filename)
                    counter = 2
                    while os.path.exists(backup_file_path):
                        backup_file_path = os.path.join(level_folder_path, category, f"{base}_{counter}{ext}")
                        counter += 1

                shutil.copy(xml_path, backup_file_path)  # Copy the XML file
                # print(f"Copied {xml_path} to {backup_file_path}")
            else:
                print(f"XML file for room {room_number} does not exist: {xml_path}")


def draw_points(PointArray, category_names, title, onclick_callback, selected_polygons, floor):
    colors = ['red', 'blue', 'green', 'orange', 'black', 'grey', 'yellow', 'pink', 'violet']  # Define colors for each set

    fig, ax = plt.subplots(figsize=(10, 8))  # Adjust the figure size here

    polygons = []
    for i, points_category in enumerate(PointArray):
        color = colors[i % len(colors)]
        category_polygons = []
        for points in points_category:
            room_number = points[0][0]  # Get the room number
            room_file_path = points[0][1]

            if room_number is not None:
                if room_number in BuildingMap:
                    # Initialize as a list if it's not already
                    if BuildingMap[room_number] is None:
                        BuildingMap[room_number] = []
                    BuildingMap[room_number].append(room_file_path)
                else:
                    BuildingMap[room_number] = [room_file_path]

            points = np.array(points[1:])
            polygon = plt.Polygon(points, closed=True, fill=True, edgecolor=color, facecolor=color, alpha=0.5, linewidth=3.5)
            category_polygons.append((polygon, room_number))
            ax.add_patch(polygon)
            plt.plot(points[:, 0], points[:, 1], marker='.', color='black')
        polygons.append(category_polygons)


    # Pass the floor to create_xml_backup_folder
    create_new_xml_folder(BuildingMap, floor)

    # Highlight selected polygons
    for selected_polygon in selected_polygons:
        selected_polygon.set_edgecolor('gray')
        selected_polygon.set_facecolor('gray')

    plt.title(title)
    legend_handles = [plt.Line2D([0], [0], color=colors[i % len(colors)], linewidth=4.5, label=category_names[i]) for i in range(len(PointArray))]
    plt.legend(handles=legend_handles, loc='best')

    fig.canvas.mpl_connect('button_press_event', lambda event: onclick_callback(event, polygons, category_names))
    return fig

class CustomDialog(simpledialog.Dialog):
    def __init__(self, master, room_name):
        self.room_name = room_name
        super().__init__(master)

    def body(self, master):
        tk.Label(master, text=f"Enter new name for Room: {self.room_name}").pack(pady=5)
        self.entry = tk.Entry(master, width=30)  # Wider entry
        self.entry.pack(pady=5)

    def apply(self):
        self.result = self.entry.get()

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.selected_polygons = []
        self.original_colors = {}
        self.current_floor = None  # Initialize current floor as None

        super().__init__(*args, **kwargs)
        self.title("UofA Building 2D UI")
        self.geometry("1200x900")
        self.resizable(True, True)

        # Configure row and column weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a container
        self.container = ttk.Frame(self)
        self.container.grid(padx=10, pady=10, sticky="nsew")

        # Configure row and column weights of the container
        self.container.grid_rowconfigure(0, weight=0)  # Row for welcome label
        self.container.grid_rowconfigure(1, weight=0)  # Row for button frame
        self.container.grid_rowconfigure(2, weight=1)  # Row for canvas
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)  # Optional: Add weight to the logo column
        # Add a welcome message
        self.welcome_label = tk.Label(self.container, text="Welcome to UofA " + BuildingName + " Architecture UI",
                                      font=("Helvetica", 24, "bold"), anchor="center")
        self.welcome_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="nsew")  # Centered at the top

        # Create button frame
        button_frame = ttk.Frame(self.container)
        button_frame.grid(row=1, column=0, pady=20, sticky="nsew")  # Positioned below the welcome label

        # Add buttons for each floor
        floors = [1, 2, 3, 4]
        for floor in floors:
            button = ttk.Button(button_frame, text=f"Floor {floor}", command=lambda f=floor: self.plot_floor_map(f))
            button.pack(side=tk.LEFT, padx=(10, 5))  # Add padding between buttons


        # Create the canvas holder frame
        self.canvas_frame = ttk.Frame(self.container)
        self.canvas_frame.grid(row=2, column=0, sticky="nsew")  # Canvas expands to fill available space

        # Adding a button to quit the application
        quit_button = ttk.Button(self.container, text="Quit", command=self.quit)
        quit_button.grid(row=3, column=0, pady=10, sticky="ew")  # Positioned below the canvas

        # Create CheckRoomNameErrors button, initially hidden
        self.check_errors_button = ttk.Button(self.container, text="Check Room Name Errors",
                                              command=self.check_room_name_errors)
        self.check_errors_button.grid(row=1, column=1, pady=10, padx=(0, 10),
                                      sticky='ne')  # Positioned to the right of the button frame
        self.check_errors_button.grid_remove()  # Hide the button initially

        # Placeholder for selected rooms for door addition
        self.selected_rooms = []

    def check_room_name_errors(self):
        # Logic to check room name errors
        print("Checking for irregular room name....." + "\n")

        # Define the project directory and the path to the new XML folder
        project_directory = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
        backup_folder_path = os.path.join(project_directory, "new_xml")

        # Get the current floor
        current_floor = self.get_current_floor()  # You may need to implement this method
        level_folder_path = os.path.join(backup_folder_path, f"Level_{current_floor}")

        # Path to the "X" folder
        x_folder_path = os.path.join(level_folder_path, "X")

        # Check if the "X" folder exists
        if os.path.exists(x_folder_path):
            # Iterate through each XML file in the "X" folder
            for xml_file in os.listdir(x_folder_path):
                if xml_file.endswith(".xml"):
                    room_name = os.path.splitext(xml_file)[0]  # Get the room name without the .xml extension
                    self.correct_room_name(room_name)  # Call the function to correct the room name
            # Show completion message after processing all files
            messagebox.showinfo("Process Completed", "Checked all files with irregular names.")
        else:
            print(f"No 'X' folder found for floor {current_floor}.")

    def plot_floor_map(self, floor):
        self.current_floor = floor  # Set the current floor
        self.check_errors_button.grid()  # Make the button visible

        # Hide welcome message and logo
        # self.welcome_label.grid_remove()

        # Clear previous canvas frame widgets
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Fetch and categorize coordinate map for the floor
        points_categories, category_names, title = self.get_floor_data(floor)

        # Create the figure
        fig = draw_points(points_categories, category_names, title, self.checkFunction, self.selected_polygons, floor)

        # Embed the figure in Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        # Add room number labels
        for points_category in points_categories:
            for points in points_category:
                room_number = points[0][0]  # Extract room number
                room_points = np.array(points[1:])  # Room polygon points
                centroid = np.mean(room_points, axis=0)  # Calculate centroid

                # Replace names with abbreviations
                if "Washroom Men" in room_number:
                    room_number = "WM"
                elif "Washroom Women" in room_number:
                    room_number = "WW"
                elif "Stairs" in room_number:
                    room_number = "S"
                elif "Entrance" in room_number:
                    room_number = "En"
                elif "Elevator" in room_number:
                    room_number = "El"
                elif "Hallway" in room_number:
                    room_number = "H"

                # Text label with a background for better readability
                plt.text(centroid[0], centroid[1], room_number, fontsize=8, ha='center', va='center',
                         color='white',
                         bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3'))

    def get_floor_data(self, floor):
        import XMLDataExtract

        def fetchCoordinateMap(floorNumber):
            return XMLDataExtract.main(floorNumber=floorNumber)

        def categorizesCoordinateMap(floorNumber: int):
            CoordinateMap = fetchCoordinateMap(floorNumber)
            # Room = CoordinateMap['Room']
            # Entrance_En = CoordinateMap['Entrance']
            # Elevator_El = CoordinateMap['Elevator']
            # Hallway_H = CoordinateMap['Hallway']
            # Washroom_WM_WW = CoordinateMap['Washroom']
            # Stair_S = CoordinateMap['Stairs']
            # XPoints = CoordinateMap['X']
            return [CoordinateMap[key] for key in CoordinateMap], [str(key) for key in CoordinateMap]

        points_categories, category_names = categorizesCoordinateMap(floor)
        print(points_categories)
        print(category_names)
        title = f'Architectural Map of Floor {floor}'

        return points_categories, category_names, title

    def get_current_floor(self):
        return self.current_floor  # Return the currently selected floor

    # Select Functions --------------------------------------------------

    def checkFunction(self, event, polygons, category_names):
        if event.inaxes is not None:
            x, y = event.xdata, event.ydata
            for category_index, category_polygons in enumerate(polygons):
                for polygon, room_number in category_polygons:
                    if polygon.get_path().contains_point((x, y)):
                        print(f"Room clicked: {room_number}")  # Print the room number
                        self.handleCheck(room_number, (x, y))

                        # Highlight the selected polygon if not already selected
                        if polygon not in self.selected_polygons:
                            self.selected_polygons.append(polygon)
                            # Remove the following lines to avoid changing the polygon color
                            # polygon.set_edgecolor('gray')
                            # polygon.set_facecolor('gray')

                        self.canvas.draw()  # Refresh the canvas
                        break

    def handleCheck(self, room_name, coordinates):
        action = simpledialog.askstring("Action", "Enter action: add_door, correct_name, or add_wall")
        print(room_name)
        if action == "add_door":
            self.add_door(room_name)
        elif action == "correct_name":
            self.correct_room_name(room_name)
        elif action == "add_wall":
            self.add_wall(coordinates)

    # 3 Main Functions --------------------------------------------------------

    def add_door(self, room_name):
        self.selected_rooms.append(room_name)
        if len(self.selected_rooms) == 2:
            # Add door logic here
            room1, room2 = self.selected_rooms
            print(f"Adding door between {room1} and {room2}")
            # Update XML
            self.update_xml_with_door(room1, room2)
            self.selected_rooms = []

    def correct_room_name(self, room_name):
        dialog = CustomDialog(self, room_name)
        new_name = dialog.result
        if new_name:
            print(f"Changing {room_name} to {new_name}")
            self.update_xml_with_new_name(room_name, new_name)

    def add_wall(self, coordinates):
        # Logic to add wall here
        point1, point2 = coordinates  # You will need to select two points
        print(f"Adding wall between {point1} and {point2}")
        # Update XML
        self.update_xml_with_wall(point1, point2)

    # Update XML Functions ---------------------------------------------------

    def update_xml_with_door(self, room1, room2):
        pass

    def update_xml_with_new_name(self, old_name, new_name):


        # Define the path to access the XML files in the new_xml folder in the project directory
        project_directory = os.path.dirname(os.path.abspath(__file__))  # Get the current project directory
        updated_folder_path = os.path.join(project_directory, "new_xml")

        # Get the current floor number
        current_floor = self.get_current_floor()
        level_folder_path = os.path.join(updated_folder_path, f"Level_{current_floor}", "X")

        try:
            # Construct the path for the old XML file
            old_xml_path = os.path.join(level_folder_path, f"{old_name}.xml")
            if not os.path.exists(old_xml_path):
                print(f"File not found: {old_xml_path}")
                return

            # Parse the original XML file
            # print(f"Parsing XML file from: {old_xml_path}")
            tree = ET.parse(old_xml_path)
            root = tree.getroot()

            # Update the XML content
            print(f"Updating XML content for room: {old_name} to {new_name}")
            root.set('name', new_name)
            root.set('key', new_name)
            for field in root.findall('.//field'):
                if field.get('key') == 'name':
                    content_element = field.find('content')
                    if content_element is not None:
                        content_element.text = new_name

            # Construct the new XML file path with versioning
            base_new_xml_path = os.path.join(level_folder_path, new_name)
            new_xml_path = f"{base_new_xml_path}.xml"
            counter = 1

            # Check for existing files and generate a new name if necessary
            while os.path.exists(new_xml_path):
                counter += 1
                new_xml_path = f"{base_new_xml_path}_{counter}.xml"

            print(f"Saving updated XML file to: {new_xml_path}" + "\n")
            tree.write(new_xml_path, encoding='utf-8', xml_declaration=True)

            # Remove the old XML file
            os.remove(old_xml_path)
            # print(f"Deleted old XML file: {old_xml_path}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def update_xml_with_wall(self, point1, point2):
        pass

