import os
import shutil
import tkinter as tk
import tkinter.messagebox as messagebox
import xml.etree.ElementTree as ET
from tkinter import simpledialog
from tkinter import ttk
from XMLDataExtract import Original_Building_Path, Edited_Building_Path, count_level_subfolders
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BuildingMap = {}
BuildingName = Original_Building_Path.split('/')[-1]


def create_edited_building_subfolders(directory_path = "Athabasca2DMapping/Buildings Data"):
    subfolders = [
        "Augustana Campus",
        "Calgary Centre",
        "Campus Saint-Jean",
        "Enterprise Square",
        "North Campus",
        "South Campus"
    ]

    edited_building_path = os.path.join(directory_path, "Edited Building")
    if not os.path.exists(edited_building_path):
        os.makedirs(edited_building_path)
        # print(f"Created: {edited_building_path}")
    # else:
        # print(f"Already exists: {edited_building_path}")

    # Create each specified subfolder within "Edited Building" if it doesn't exist
    for subfolder in subfolders:
        subfolder_path = os.path.join(edited_building_path, subfolder)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
            # print(f"Created: {subfolder_path}")
        # else:
            # print(f"Already exists: {subfolder_path}")

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
    # create_new_xml_folder(BuildingMap, floor)
    create_edited_building_subfolders(directory_path="Buildings Data")

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
    def __init__(self, building, campus, *args, **kwargs):

        # Store parameters
        self.building = building
        self.campus = campus
        self.originalXMLfolderPath = f"Buildings Data/Buildings/{self.campus}/{self.building}"
        self.editedXMLfolderPath = f"Buildings Data/Edited Building/{self.campus}/{self.building}"


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
        self.welcome_label = tk.Label(self.container, text="Welcome to UofA " + building + " Architecture UI",
                                      font=("Helvetica", 24, "bold"), anchor="center")
        self.welcome_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="nsew")  # Centered at the top

        # Create button frame
        button_frame = ttk.Frame(self.container)
        button_frame.grid(row=1, column=0, pady=20, sticky="nsew")  # Positioned below the welcome label

        # Add buttons for each floor
        floors = count_level_subfolders(Original_Building_Path, campus, building, "interior")

        if not floors:  # Check if levels is empty
            # Create and display 'No data found' label
            self.no_data_label = tk.Label(self.container, text="No data found", font=("Helvetica", 18, "italic"), fg="red")
            self.no_data_label.grid(row=1, column=0, pady=20, sticky="nsew")  # Display 'No data found' message
            button_frame.grid_remove()  # Hide button frame if no data found
        else:
            self.no_data_label = None  # Initialize to None if data is found
            for floor in floors:
                button = ttk.Button(button_frame, text=f"Floor {floor}", command=lambda f=floor: self.plot_floor_map(f, building, campus))
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
        print("Checking for irregular room name.....")

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

    def plot_floor_map(self, floor, building, campus):
        self.current_floor = floor  # Set the current floor
        self.check_errors_button.grid()  # Make the button visible

        # Hide welcome message and logo
        # self.welcome_label.grid_remove()

        # Clear previous canvas frame widgets
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Fetch and categorize coordinate map for the floor
        points_categories, category_names, title = self.get_floor_data(floor, building, campus)

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

    def get_floor_data(self, floor, building, campus):
        import XMLDataExtract

        def fetchCoordinateMap(floorNumber):
            return XMLDataExtract.main(floorNumber, building, campus)

        def categorizesCoordinateMap(floorNumber):
            CoordinateMap = fetchCoordinateMap(floorNumber)
            return [CoordinateMap[key] for key in CoordinateMap], [str(key) for key in CoordinateMap]

        points_categories, category_names = categorizesCoordinateMap(floor)
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
                        print(f"Room clicked: {room_number}\n")  # Print the room number
                        self.handleCheck(room_number, (x, y))

                        # Highlight the selected polygon if not already selected
                        if polygon not in self.selected_polygons:
                            self.selected_polygons.append(polygon)

                        self.canvas.draw()  # Refresh the canvas
                        break

    def handleCheck(self, room_name, coordinates):
        action = simpledialog.askstring("Action", "Enter action: add_door, correct_name, or add_wall")
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
            print(f"Changing Room name: {room_name} to {new_name}\n")
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


    def find_xml_file_path(self, root_folder, file_name, room_name):
        room_path = os.path.join(root_folder, 'Interior', f'{self.current_floor}',room_name)
        room_path = room_path.replace('/', '\\')

        if not os.path.isdir(room_path):
            print('XML Directory does not exist:', room_path)
            return None

        for root, dirs, files in os.walk(room_path):

            if file_name in files:
                file_path = os.path.join(root, file_name).replace('\\', '/')
                return file_path

        print('xml File not found.')
        return None


    def update_xml_with_new_name(self, room_name, new_name):
        if self.current_floor is None:
            raise ValueError("Current floor is not set.")

        XML_Filename = "xml"
        original_xml_path = self.find_xml_file_path(self.originalXMLfolderPath, XML_Filename, room_name)

        if original_xml_path is None:
            raise FileNotFoundError(
                f"Original XML file '{XML_Filename}' not found in '{self.originalXMLfolderPath}'.")

        edited_folder_path = os.path.join(self.editedXMLfolderPath, self.current_floor, room_name)
        edited_xml_path = os.path.join(edited_folder_path, XML_Filename)  # Keep original filename for now

        os.makedirs(edited_folder_path, exist_ok=True)

        if not os.path.isfile(original_xml_path):
            raise FileNotFoundError(f"The path '{original_xml_path}' is not a file.")

        shutil.copy2(original_xml_path, edited_xml_path)

        try:
            tree = ET.parse(edited_xml_path)
            root = tree.getroot()

            if root.tag == 'item':
                root.set('name', new_name)
                root.set('key', new_name)

                tree.write(edited_xml_path, encoding='utf-8', xml_declaration=True)
                print(f"The item name and key have been updated successfully in {room_name}.")
            else:
                print("The root element is not <item>.")
        except ET.ParseError as e:
            print(f"Failed to parse XML file: {e}")


    def update_xml_with_wall(self, point1, point2):
        pass

