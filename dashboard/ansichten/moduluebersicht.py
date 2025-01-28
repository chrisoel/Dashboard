import tkinter as tk
from tkinter import ttk

class Moduluebersicht(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        daten = self.master.logik.get_moduluebersicht_ansicht_daten()

        label = ttk.Label(self, text="Modulübersicht", font=("Arial", 16))
        label.pack(pady=10)

        tree = ttk.Treeview(self, columns=("Modulname", "Kürzel", "Status"), show="headings")
        tree.heading("Modulname", text="Modulname")
        tree.heading("Kürzel", text="Kürzel")
        tree.heading("Status", text="Status")
        tree.pack(fill=tk.BOTH, expand=True)

        for eintrag in daten:
            tree.insert("", tk.END, values=eintrag)