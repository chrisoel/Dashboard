import tkinter as tk
from tkinter import ttk

class Zeitmanagement(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        daten = self.master.logik.get_zeitmanagement_ansicht_daten()

        label = ttk.Label(self, text="Zeitmanagement", font=("Arial", 16))
        label.pack(pady=10)

        for eintrag in daten:
            eintrag_label = ttk.Label(self, text=f"Arbeitstage: {eintrag[1]}, Zeitmodell: {eintrag[2]}")
            eintrag_label.pack(pady=5)