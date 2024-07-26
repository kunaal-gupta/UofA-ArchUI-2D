import MapDesign


if __name__ == '__main__':
    campus = input('Enter Campus Name: ').title()
    building = input(f'Enter Building Name in {campus}: ').title()
    # campus = 'North Campus'
    # building = 'Athabasca Hall'

    print()
    print("Building User interface.....")
    print('Fetching data....\n')

    app = MapDesign.Application(building, campus)
    app.mainloop()