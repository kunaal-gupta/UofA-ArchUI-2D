class Application(tk.Tk):
    def __init__(self, building, campus, *args, **kwargs):
        # Initialization code as before
        self.legend_window = None  # To track the legend window instance
        super().__init__(*args, **kwargs)

    def plot_floor_map(self, floor, building, campus):
        self.current_floor = floor
        self.check_errors_button.grid()
        self.generate_neighbours_button.grid()
        self.add_wall_button.grid()

        # Close the previous legend window if it exists
        if self.legend_window is not None and self.legend_window.winfo_exists():
            self.legend_window.destroy()

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        points_categories, category_names, title = self.get_floor_data(floor, building, campus)
        fig, room_colors, colors = draw_points(points_categories, category_names, title, self.onCanvasClick,
                                               self.selected_polygons, floor)

        self.polygons = []
        for category_polygons in points_categories:
            for points in category_polygons:
                room_number = points[0][0]
                polygon_points = np.array(points[1:])
                polygon = plt.Polygon(polygon_points, closed=True, fill=True, edgecolor='black', facecolor='red',
                                      alpha=0.5)
                self.polygons.append((polygon, room_number))

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

        # Show legend in a new window with the floor number in the title
        self.legend_window = show_legend_window(colors, category_names, floor)

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


def show_legend_window(colors, category_names, floor):
    legend_window = tk.Toplevel()
    legend_window.title(f"Legend - Floor {floor}")
    legend_window.geometry("300x400")

    fig, ax = plt.subplots(figsize=(3, 4))
    ax.axis('off')  # Hide the axes

    legend_handles = [plt.Line2D([0], [0], color=colors[i % len(colors)], linewidth=4.5, label=category_names[i])
                      for i in range(len(category_names))]
    ax.legend(handles=legend_handles, loc='center')

    canvas = FigureCanvasTkAgg(fig, master=legend_window)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both")

    return legend_window
