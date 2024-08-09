import os
import shutil
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import ttk
from RoomManager import RoomManager
from XMLDataExtract import Original_Building_Path, Edited_Building_Path, count_level_subfolders, \
    parse_xml_for_roomnumber_and_floor, parse_xml_for_coordinates, turtleConverter
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from DialogueBox import CustomDialog

BuildingMap = {}
BuildingName = Original_Building_Path.split('/')[-1]
updatedRowsArray = []

RoomsDataArray = []

def create_edited_building_subfolders(directory_path="Athabasca2DMapping/Buildings Data"):
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

    for subfolder in subfolders:
        subfolder_path = os.path.join(edited_building_path, subfolder)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)



def draw_points(PointArray, category_names, title, onclick_callback, selected_polygons, floor):
    global RoomsDataArray
    colors = ['red', 'blue', 'green', 'orange', 'maroon', 'grey', 'yellow', 'pink', 'violet']

    fig, ax = plt.subplots(figsize=(10, 8))

    polygons = []
    room_colors = []

    for i, points_category in enumerate(PointArray):
        for j in points_category:
            RoomsDataArray.append(j)
        color = colors[i % len(colors)]
        category_polygons = []

        for points in points_category:
            room_number = points[0][0]
            room_file_path = points[0][1]

            if room_number is not None:
                if room_number in BuildingMap:
                    if BuildingMap[room_number] is None:
                        BuildingMap[room_number] = []
                    BuildingMap[room_number].append(room_file_path)
                else:
                    BuildingMap[room_number] = [room_file_path]

            points = np.array(points[1:])
            polygon = plt.Polygon(points, closed=True, fill=True, edgecolor=color, facecolor=color, alpha=0.5,
                                  linewidth=3.5)
            category_polygons.append((polygon, room_number))
            ax.add_patch(polygon)
            plt.plot(points[:, 0], points[:, 1], marker='.', color='black')

            room_colors.append((room_number, color))

        polygons.append(category_polygons)

    create_edited_building_subfolders(directory_path="Buildings Data")

    for selected_polygon in selected_polygons:
        selected_polygon.set_edgecolor('gray')
        selected_polygon.set_facecolor('gray')

    plt.title(title)
    legend_handles = [plt.Line2D([0], [0], color=colors[i % len(colors)], linewidth=4.5, label=category_names[i]) for i
                      in range(len(PointArray))]
    plt.legend(handles=legend_handles, loc='best')

    fig.canvas.mpl_connect('button_press_event', lambda event: onclick_callback(event, polygons, category_names))
    return fig, room_colors


def get_initials(text):
    try:
        int(text)
        return text
    except ValueError:
        words = text.split()
        initials = []

        for word in words:
            if word.isdigit():
                initials.append(word)
            else:
                initials.append(word[0].upper())

        return ''.join(initials)

class Application(tk.Tk):
    def __init__(self, building, campus, *args, **kwargs):

        self.canvas = None
        self.adding_door = False
        self.building = building
        self.campus = campus
        self.originalXMLfolderPath = f"Buildings Data/Buildings/{self.campus}/{self.building}"
        self.editedXMLfolderPath = f"Buildings Data/Edited Building/{self.campus}/{self.building}"
        self.selected_polygons = []
        self.original_colors = {}
        self.current_floor = None
        super().__init__(*args, **kwargs)
        self.title("UofA Building 2D UI")
        self.geometry("1200x900")
        self.resizable(True, True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = ttk.Frame(self)
        self.container.grid(padx=10, pady=10, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=0)
        self.container.grid_rowconfigure(1, weight=0)
        self.container.grid_rowconfigure(2, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.welcome_label = tk.Label(self.container, text="Welcome to UofA " + building + " Architecture UI",
                                      font=("Helvetica", 24, "bold"), anchor="center")
        self.welcome_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="nsew")
        button_frame = ttk.Frame(self.container)
        button_frame.grid(row=1, column=0, pady=20, sticky="nsew")
        floors = count_level_subfolders(Original_Building_Path, campus, building, "interior")

        if not floors:
            self.no_data_label = tk.Label(self.container, text="No data found", font=("Helvetica", 18, "italic"),
                                          fg="red")
            self.no_data_label.grid(row=1, column=0, pady=20, sticky="nsew")
            button_frame.grid_remove()
        else:
            self.no_data_label = None
            for floor in floors:
                button = ttk.Button(button_frame, text=f"Floor {floor}",
                                    command=lambda f=floor: self.plot_floor_map(f, building, campus))
                button.pack(side=tk.LEFT, padx=(10, 5))

        self.canvas_frame = ttk.Frame(self.container)
        self.canvas_frame.grid(row=2, column=0, sticky="nsew")

        quit_button = ttk.Button(self.container, text="Quit", command=self.quit)
        quit_button.grid(row=3, column=0, pady=10, sticky="ew")

        self.check_errors_button = ttk.Button(self.container, text="Check Room Name", command=self.correct_room_name)
        self.check_errors_button.grid(row=1, column=1, pady=10, padx=(0, 10), sticky='ne')
        self.check_errors_button.grid_remove()

        self.add_wall_button = ttk.Button(self.container, text="Generate Neighbours Data", command=self.calling_generating_neigbours_func)
        self.add_wall_button.grid(row=2, column=1, pady=10, padx=(1, 0), sticky='ne')
        self.add_wall_button.grid_remove()


        self.selected_rooms = []

    def plot_floor_map(self, floor, building, campus):
        self.current_floor = floor
        self.check_errors_button.grid()
        self.add_wall_button.grid()

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        points_categories, category_names, title = self.get_floor_data(floor, building, campus)
        fig, room_colors = draw_points(points_categories, category_names, title, self.onCanvasClick,
                                       self.selected_polygons, floor)

        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        for points_category in points_categories:
            for points in points_category:
                room_number = points[0][0]
                room_points = np.array(points[1:])
                centroid = np.mean(room_points, axis=0)
                room_label = get_initials(room_number)

                label_color = next((color for rn, color in room_colors if rn == room_number), 'black')

                plt.text(centroid[0], centroid[1], room_label, fontsize=10, ha='center', va='center',
                         color='black', fontweight='bold',
                         bbox=dict(facecolor=label_color, alpha=0.7, edgecolor=label_color, boxstyle='round,pad=0.3'))

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

    def onCanvasClick(self, event, polygons, category_names):
        if event.inaxes is not None:
            x, y = event.xdata, event.ydata
            print(f"Coordinates: ({x}, {y})")

            for category_index, category_polygons in enumerate(polygons):
                for polygon, room_number in category_polygons:
                    if polygon.get_path().contains_point((x, y)):
                        if room_number != "Building Outline":
                            print(f"Room clicked: {room_number}" + "\n")
                            if polygon not in self.selected_polygons:
                                self.selected_polygons.append(polygon)
                            self.canvas.draw()
                            return

        print("Event not in axes or no polygon contains the point" + "\n")

    def correct_room_name(self):
        self.update_xml_with_new_name()

    def find_xml_file_path(self, root_folder, file_name='xml', roomname='X'):
        room_path = os.path.join(root_folder, 'Interior', f'{self.current_floor}', roomname)
        room_path = room_path.replace('/', '\\')

        if not os.path.isdir(room_path):
            print('XML Directory does not exist:', room_path)
            return None

        filePathArray = []
        for root, dirs, files in os.walk(room_path):
            if file_name in files:
                if file_name == 'xml':
                    file_path = os.path.join(root, file_name).replace('\\', '/')
                    filePathArray.append(file_path)

        return filePathArray

    def update_xml_with_new_name(self):
        if self.current_floor is None:
            raise ValueError("Current floor is not set.")
        XML_Filename = "xml"
        room_name = 'X'
        original_xml_path_array = self.find_xml_file_path(self.originalXMLfolderPath, XML_Filename, room_name)

        for i in original_xml_path_array:
            print()
            if i is None:
                raise FileNotFoundError(
                    f"Original XML file '{XML_Filename}' not found in '{self.originalXMLfolderPath}'.")

            x_position = i.find('X/') + len('X/')
            xml_file_path = i[x_position:]

            temp = i[x_position:]

            edited_folder_path = os.path.join(self.editedXMLfolderPath, 'Interior', self.current_floor, room_name,
                                              xml_file_path)
            edited_xml_path = os.path.join(edited_folder_path, XML_Filename)

            os.makedirs(edited_folder_path, exist_ok=True)

            if not os.path.isfile(i):
                raise FileNotFoundError(f"The path '{i}' is not a file.")

            shutil.copy2(i, edited_xml_path)

            root = tk.Tk()
            root.withdraw()

            dialog = CustomDialog(root, temp)
            new_name = dialog.result

            try:
                tree = ET.parse(edited_xml_path)
                root = tree.getroot()

                if root.tag == 'item':
                    root.set('name', new_name)
                    root.set('key', new_name)

                    tree.write(edited_xml_path, encoding='utf-8', xml_declaration=True)
                    print(f"The item name and key have been updated successfully in {room_name} to {new_name}.")
                else:
                    print("The root element is not <item>.")

                self.update_records(self.building, self.campus, self.current_floor, new_name, edited_xml_path)

            except ET.ParseError as e:
                print(f"Failed to parse XML file: {e}")
        self.Update_TurtleOuput('TurtleOutput.txt', self.building, self.campus, self.current_floor, 'X')

    def update_records(self, building, campus, floor, room, file):

        global updatedRowsArray
        RoomNumber, Level = parse_xml_for_roomnumber_and_floor(file)
        coordinateList = parse_xml_for_coordinates(file)
        turtleData = turtleConverter(building, campus, floor, room, coordinateList) + '\n'
        updatedRowsArray.append(turtleData)

    def Update_TurtleOuput(self, file_path, building, campus, floor, room):

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            filtered_lines = []
            for line in lines:
                if not (f"Building: {building}, Campus: {campus}, Floor: {floor}, Room: {room}" in line):
                    filtered_lines.append(line)

            filtered_lines += updatedRowsArray

            with open(file_path, 'w') as file:
                file.writelines(filtered_lines)

            print("\n" + "Records updated successfully." + "\n")

        except FileNotFoundError:
            print(f"The file {file_path} does not exist.")
        except IOError as e:
            print(f"An error occurred while accessing the file: {e}")

    def calling_generating_neigbours_func(self):
        global RoomsDataArray

        room_manager = RoomManager(RoomsDataArray, self.campus, self.building, self.current_floor)
        room_manager.generating_neighbours()

