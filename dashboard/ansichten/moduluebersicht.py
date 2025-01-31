import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import logging

class Moduluebersicht(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Moduluebersicht")

        self.ects_werte = ["5", "10"]
        self.semester_werte = [str(i) for i in range(1, 13)]

        self.logger.info("📌 Modulübersicht geladen.")
        self.erstelle_gui()
        self.lade_daten()

    def erstelle_gui(self):
        """Erstellt das Hauptlayout für die Modulübersicht."""
        ttk.Label(self, text="📚 Modulübersicht", font=("Arial", 16)).pack(pady=10)

        self.tree = ttk.Treeview(
            self, columns=("ID", "Semester", "Modulname", "Kürzel", "Status", "ECTS", "Startdatum"), show="headings"
        )
        for spalte in ("ID", "Semester", "Modulname", "Kürzel", "Status", "ECTS", "Startdatum"):
            self.tree.heading(spalte, text=spalte)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="➕ Modul hinzufügen", command=self.modul_hinzufuegen_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Modul bearbeiten", command=self.modul_bearbeiten_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Modul löschen", command=self.modul_loeschen).pack(side=tk.LEFT, padx=5)

    def lade_daten(self):
        """Lädt die Moduldaten aus der Datenbank."""
        self.daten = self.master.logik.get_moduluebersicht_ansicht_daten()
        self.logger.info(f"📊 Geladene Moduldaten: {self.daten}")
        for eintrag in self.daten:
            self.tree.insert("", tk.END, values=eintrag)

    def modul_hinzufuegen_popup(self):
        """Öffnet das Modul-Hinzufügen-Popup."""
        self.logger.info("📌 Öffne Modul-Hinzufügen-Dialog.")
        self.erstelle_popup("Neues Modul hinzufügen", "INSERT")

    def modul_bearbeiten_popup(self):
        """Öffnet das Modul-Bearbeiten-Popup."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Fehler", "Bitte ein Modul auswählen.")
            return

        values = self.tree.item(selected_item, "values")
        self.logger.info(f"✏️ Öffne Modul-Bearbeiten-Dialog für ID {values[0]}")
        self.erstelle_popup("Modul bearbeiten", "UPDATE", values)

    def erstelle_popup(self, titel, aktion, modulwerte=None):
        """Erstellt ein Popup-Fenster für Modul-Eingaben."""
        popup = tk.Toplevel(self)
        popup.title(titel)
        popup.geometry("400x600")

        self.semester_combobox = self.erstelle_dropdown(popup, "Semester-ID:", self.semester_werte)
        self.modulname_entry = self.erstelle_entry(popup, "Modulname:")
        self.kuerzel_entry = self.erstelle_entry(popup, "Kürzel:")
        self.status_combobox = self.erstelle_dropdown(popup, "Status:", ["Offen", "In Bearbeitung", "Abgeschlossen"])
        self.ects_combobox = self.erstelle_dropdown(popup, "ECTS-Punkte:", self.ects_werte)

        ttk.Label(popup, text="Startdatum auswählen:").pack(pady=5)
        self.kalender = Calendar(popup, selectmode="day", date_pattern="yyyy-mm-dd")
        self.kalender.pack(pady=5)

        if modulwerte:
            self.semester_combobox.set(str(modulwerte[1]))
            self.modulname_entry.insert(0, modulwerte[2])
            self.kuerzel_entry.insert(0, modulwerte[3])
            self.status_combobox.set(modulwerte[4])
            self.ects_combobox.set(str(modulwerte[5]))
            self.kalender.set_date(modulwerte[6])

        ttk.Button(
            popup, text="💾 Speichern",
            command=lambda: self.modul_speichern(popup, aktion, modulwerte[0] if modulwerte else None)
        ).pack(pady=10)

    def erstelle_entry(self, popup, text):
        """Erstellt ein Eingabefeld mit Label."""
        ttk.Label(popup, text=text).pack(pady=5)
        entry = ttk.Entry(popup)
        entry.pack(pady=5)
        return entry

    def erstelle_dropdown(self, popup, text, values):
        """Erstellt ein Dropdown-Menü mit Label."""
        ttk.Label(popup, text=text).pack(pady=5)
        dropdown = ttk.Combobox(popup, values=values, state="readonly")
        dropdown.pack(pady=5)
        return dropdown

    def modul_speichern(self, popup, aktion, modul_id):
        """Validiert Eingaben und speichert das Modul."""
        daten = self.validiere_eingaben()
        if not daten:
            return

        if aktion == "UPDATE":
            daten = (modul_id, *daten)

        erfolg = self.master.logik.set_moduluebersicht_ansicht_daten(aktion, daten)

        if erfolg:
            self.logger.info(f"✅ Modul erfolgreich gespeichert: {daten}")
            messagebox.showinfo("Erfolg", f"Modul erfolgreich {aktion.lower()}!")
            popup.destroy()
            self.tree.delete(*self.tree.get_children())
            self.lade_daten()
        else:
            self.logger.error("❌ Fehler beim Speichern des Moduls.")
            messagebox.showerror("Fehler", "Modul konnte nicht gespeichert werden.")

    def validiere_eingaben(self):
        """Überprüft die Benutzereingaben auf Korrektheit."""
        semester_id = self.semester_combobox.get()
        modulname = self.modulname_entry.get().strip()
        kuerzel = self.kuerzel_entry.get().strip()
        status = self.status_combobox.get()
        ects = self.ects_combobox.get()
        startdatum = self.kalender.get_date()

        if not all([semester_id, modulname, kuerzel, status, ects, startdatum]):
            messagebox.showerror("Fehler", "Bitte alle Pflichtfelder ausfüllen!")
            return None

        return (int(semester_id), modulname, kuerzel, status, int(ects), startdatum)

    def modul_loeschen(self):
        """Löscht ein Modul."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Fehler", "Bitte ein Modul auswählen.")
            return

        modul_id = self.tree.item(selected_item, "values")[0]
        if self.master.logik.set_moduluebersicht_ansicht_daten("DELETE", (modul_id,)):
            self.tree.delete(selected_item)
            self.logger.info(f"✅ Modul mit ID {modul_id} gelöscht.")
        else:
            messagebox.showerror("Fehler", "Das Modul konnte nicht gelöscht werden.")