import os
from tkinter import simpledialog, Tk


class RoomManager:
    def __init__(self, rooms, campus, building, floor):
        self.rooms = rooms
        self.campus = campus
        self.building = building
        self.floor = floor

    def are_neighbouring_rooms(self, room1, room2):
        from FindingNeigbour import Neighbours
        neighbours = Neighbours()
        return neighbours.are_rooms_neighbors(room1, room2)

    def generating_neighbours(self):
        root = Tk()
        root.withdraw()

        default_file_name = 'OutputFiles/NeighboringRooms.txt'
        os.makedirs(os.path.dirname(default_file_name), exist_ok=True)

        file_name = simpledialog.askstring(
            "File Name",
            f"Enter file name to store neighboring rooms data. Default filename {os.path.basename(default_file_name)}:",
            initialvalue=os.path.basename(default_file_name)
        )

        if not file_name:
            file_name = os.path.basename(default_file_name)
        output_file = os.path.join(os.path.dirname(default_file_name), file_name)

        try:
            with open(output_file, 'a+') as file:
                file.seek(0)
                if file.read(1):
                    file.seek(0, 2)
                    print(f'{output_file} file already exists')
                    print(f'Appending neighbouring rooms\' data to {output_file}')
                else:
                    print(f'Created {output_file} to store neighboring rooms data. Processing file...')

                for i in range(len(self.rooms)):
                    for j in range(i + 1, len(self.rooms)):
                        room1_name = self.rooms[i][0][0]
                        room1 = self.rooms[i][1:]
                        room2_name = self.rooms[j][0][0]
                        room2 = self.rooms[j][1:]

                        if self.are_neighbouring_rooms(room1, room2):
                            file.write(
                                "{" + f"Campus: {self.campus}, Building: {self.building}, Floor: {self.floor}, Neighbors: [{room1_name} & {room2_name}]" + "}" + "\n")

        except IOError as e:
            print(f"An error occurred while handling the file: {e}")

        print(f"Neighboring rooms for {self.building} - [{self.floor}] have been written to {output_file}.\n")
