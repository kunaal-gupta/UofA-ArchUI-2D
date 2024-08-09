from tkinter import simpledialog, Label, Entry

class CustomDialog(simpledialog.Dialog):
    def __init__(self, master, room_name, dialog_title="Default Title"):
        self.room_name = room_name
        self._dialog_title = dialog_title  # Renamed to avoid conflict
        super().__init__(master, title=self._dialog_title)

    def body(self, master):
        Label(master, text=f"Enter new name for Room: {self.room_name}").pack(pady=5)
        self.entry = Entry(master, width=30)
        self.entry.pack(pady=5)

    def apply(self):
        self.result = self.entry.get()
