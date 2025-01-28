import tkinter as tk
from tkinter import ttk

class Einstellungen(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        daten = self.master.logik.get_einstellungen_ansicht_daten()

        label = ttk.Label(self, text="Einstellungen", font=("Arial", 16))
        label.pack(pady=10)

        for eintrag in daten:
            eintrag_label = ttk.Label(self, text=f"Studiengang: {eintrag[0]}, Startdatum: {eintrag[1]}")
            eintrag_label.pack(pady=5)