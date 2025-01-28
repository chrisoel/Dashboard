import tkinter as tk
from tkinter import ttk

class Startbildschirm(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        daten = self.master.logik.get_startbildschirm_ansicht_daten()

        label = ttk.Label(self, text="Startbildschirm", font=("Arial", 16))
        label.pack(pady=10)

        tree = ttk.Treeview(self, columns=("Name", "Startdatum"), show="headings")
        tree.heading("Name", text="Studiengang")
        tree.heading("Startdatum", text="Startdatum")
        tree.pack(fill=tk.BOTH, expand=True)

        for eintrag in daten:
            tree.insert("", tk.END, values=eintrag)