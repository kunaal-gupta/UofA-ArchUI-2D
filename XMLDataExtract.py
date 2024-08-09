import os
import xml.etree.ElementTree as ET

Original_Building_Path = "Buildings Data/Buildings/"
Edited_Building_Path = "Buildings Data/Edited Building/"


filesArray = []
Data = []


def fetch_XML_file_paths(directory, floor):
    filesArray = []
    interior_path = os.path.join(directory, 'interior').replace('\\', '/')
    level_folder = f'Level {floor}'

    for root, dirs, files in os.walk(interior_path):
        for dir_name in dirs:
            if dir_name == level_folder:
                level_path = os.path.join(root, dir_name).replace('\\', '/')
                for level_root, level_dirs, level_files in os.walk(level_path):
                    for file in level_files:
                        filepath = os.path.join(level_root, file).replace('\\', '/')
                        if filepath.endswith("xml"):
                            filesArray.append(filepath)
                return filesArray
    print(filesArray)
    return filesArray


def parse_xml_for_coordinates(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    coordinate_list_field = root.find(".//field[@key='coordinate list']")
    coordinate_output_list = []

    if coordinate_list_field is not None:
        coordinate_list = coordinate_list_field.find('content').text
        coordinates = coordinate_list.split('|')
        for coord in coordinates:
            x, _, z = coord.split(',')
            coordinate_output_list.append([float(x), float(z)])

        return coordinate_output_list


def parse_floor_number(text):
    path_parts = text.split('/')
    Level = int()
    for path in path_parts:
        if 'Level' in path:
            Level = path.split()[-1]

    return Level

def polygon_centroid(vertices):
    if vertices is not None:
        n = len(vertices)
        area = 0
        centroid_x = 0
        centroid_y = 0

        for i in range(n):
            current_vertex = vertices[i]
            next_vertex = vertices[(i + 1) % n]
            cross_product = (current_vertex[0] * next_vertex[1]) - (next_vertex[0] * current_vertex[1])
            area += cross_product
            centroid_x += (current_vertex[0] + next_vertex[0]) * cross_product
            centroid_y += (current_vertex[1] + next_vertex[1]) * cross_product

        if area == 0:
            return None

        area /= 2.0
        centroid_x /= (6 * area)
        centroid_y /= (6 * area)

        return round(centroid_x, 5), round(centroid_y, 5)

def parse_xml_for_roomnumber_and_floor(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    room_number_element = root.find("./fields/field[@key='name']/content")
    if room_number_element is not None:
        room_number = room_number_element.text
        return room_number, parse_floor_number(xml_file)
    return None, parse_floor_number(xml_file)


def parse_xml_for_type(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    field = root.find(".//field[@key='name']/content")

    if field is not None:
        try:
            a = int(parse_xml_for_roomnumber_and_floor(xml_file))
            return str(a)

        except:
            return field.text


def count_level_subfolders(base_directory, building, campus, interior_folder):
    base_directory += building + '/' + campus

    try:
        interior_path = os.path.join(base_directory, interior_folder)
        if not os.path.isdir(interior_path):
            print(f"The interior folder '{interior_folder}' does not exist in '{base_directory}'.")
            return 0

        entries = os.listdir(interior_path)
        level_subfolders = [entry for entry in entries if
                            os.path.isdir(os.path.join(interior_path, entry)) and entry.startswith('Level ')]

        return level_subfolders
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

def turtleConverter(building, campus, floor, RoomNumber, coordinateList: list):
    row = f"Building: {building}, Campus: {campus}, Floor: {floor}, Room: {RoomNumber}, Centroid: {polygon_centroid(coordinateList)}"
    row = "{"+row+"}"
    return row


import os

def main(floor, building, campus):
    global path
    path = Original_Building_Path + campus + '/' + building

    floorNumber = floor.split()[-1]
    files = fetch_XML_file_paths(path, floorNumber)
    CoordinatesMap = {}

    output_file = 'OutputFiles/TurtleOutput.txt'

    directory = os.path.dirname(output_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    existing_lines = set()
    if os.path.exists(output_file):
        with open(output_file, 'r') as file_output:
            existing_lines = set(file_output.readlines())

    with open(output_file, 'a') as file_output:
        newDataCheck = False
        for file in files:
            RoomNumber, Level = parse_xml_for_roomnumber_and_floor(file)
            coordinateList = parse_xml_for_coordinates(file)
            turtleData = turtleConverter(building, campus, floor, RoomNumber, coordinateList) + '\n'

            if turtleData not in existing_lines:
                newDataCheck = True
                file_output.write(turtleData)
                existing_lines.add(turtleData)

            if coordinateList is not None:
                coordinateList.insert(0, [RoomNumber.replace('-', ''), file])
                type_key = str(parse_xml_for_type(file).strip())
                if type_key not in CoordinatesMap:
                    CoordinatesMap[type_key] = []
                CoordinatesMap[type_key].append(coordinateList)

    if newDataCheck:
        print(f'Appended turtle data - {building} [{floor}] in {output_file} file')
    return CoordinatesMap
