import MapDesign


if __name__ == '__main__':
    campus = input('Enter Campus Name: ').title()
    building = input('Enter Building Name: ').title()
    print()
    print("Building Data.....")

    app = MapDesign.Application(building, campus)
    app.mainloop()