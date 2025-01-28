import tkinter as tk
from tkinter import ttk

class Studienfortschritt(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        daten = self.master.logik.get_studienfortschritt_ansicht_daten()

        label = ttk.Label(self, text="Studienfortschritt", font=("Arial", 16))
        label.pack(pady=10)

        for semester in daten:
            semester_label = ttk.Label(self, text=f"Semester {semester[0]}: {semester[1]} - Note: {semester[2]}")
            semester_label.pack(pady=5)