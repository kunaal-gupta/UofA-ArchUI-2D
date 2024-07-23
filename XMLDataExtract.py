import os
import xml.etree.ElementTree as ET

# directory_path = "C:/Users/kunaa/Downloads/Athabasca Hall/Athabasca Hall/"
directory_path = "C:/Users/kunaa/Downloads/Buildings/Buildings/North Campus/Cameron Library"

filesArray = []
Data = []


# {Type: Room, Level: 1, RoomNumber: 101, CentralPoint: 34}

def fetch_XML_file_paths(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file).replace('\\', '/')
            if filepath.split('/')[-1] == 'xml':
                filesArray.append(filepath)
    return filesArray


def polygon_centroid(vertices):
    if vertices is not None:
        # Number of vertices
        n = len(vertices)

        # Initialize variables to store area and centroid coordinates
        area = 0
        centroid_x = 0
        centroid_y = 0

        # Iterate over each pair of vertices
        for i in range(n):
            # Current vertex
            current_vertex = vertices[i]

            # Next vertex (if current vertex is the last one, wrap around to the first vertex)
            next_vertex = vertices[(i + 1) % n]

            # Compute the cross-product of current and next vertex coordinates
            cross_product = (current_vertex[0] * next_vertex[1]) - (next_vertex[0] * current_vertex[1])

            # Update the area
            area += cross_product

            # Update centroid coordinates
            centroid_x += (current_vertex[0] + next_vertex[0]) * cross_product
            centroid_y += (current_vertex[1] + next_vertex[1]) * cross_product

        # Check if area is zero
        if area == 0:
            return None  # Handle degenerate polygon

        # Calculate the final area and centroid coordinates
        area /= 2.0
        centroid_x /= (6 * area)
        centroid_y /= (6 * area)

        return round(centroid_x, 5), round(centroid_y, 5)


def parse_xml_for_coordinates(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the 'coordinate list' field
    coordinate_list_field = root.find(".//field[@key='coordinate list']")
    coordinate_output_list = []

    if coordinate_list_field is not None:
        # Extract the content of the 'coordinate list' field
        coordinate_list = coordinate_list_field.find('content').text

        # Split the coordinate list by '|'
        coordinates = coordinate_list.split('|')

        # Extract x and z coordinates for each point

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

    # Find the field element with key='name'
    field = root.find(".//field[@key='name']/content")

    # Check if the field element exists
    if field is not None:
        try:
            int(parse_xml_for_roomnumber_and_floor(xml_file)[0].split('-')[0])
            return 'Room'

        except:
            return field.text


def count_level_subfolders(base_directory, interior_folder):
    try:
        interior_path = os.path.join(base_directory, interior_folder)
        if not os.path.isdir(interior_path):
            print(f"The interior folder '{interior_folder}' does not exist in '{base_directory}'.")
            return 0

        entries = os.listdir(interior_path)
        level_subfolders = [entry for entry in entries if
                            os.path.isdir(os.path.join(interior_path, entry)) and entry.startswith('Level ')]
        print(f"Filtered level subfolders: {level_subfolders}")

        return len(level_subfolders), level_subfolders
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0


countLevels, LevelName = count_level_subfolders(directory_path, "interior")


def main(floorNumber: int):
    files = fetch_XML_file_paths(directory_path)
    CoordinatesMap = {}

    for file in files:
        RoomNumber, Level = parse_xml_for_roomnumber_and_floor(file)
        coordinateList = parse_xml_for_coordinates(file)

        if coordinateList is not None:
            coordinateList.insert(0, [RoomNumber.replace('-', ''), file])
            if int(Level) == floorNumber:
                if str(parse_xml_for_type(file).strip().split()[0]) in CoordinatesMap:
                    CoordinatesMap[str(parse_xml_for_type(file).strip().split()[0])].append(coordinateList)
                else:
                    CoordinatesMap[str(parse_xml_for_type(file).strip().split()[0])] = list()
    return CoordinatesMap

# main(1)
