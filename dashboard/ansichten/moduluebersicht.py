import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import logging

class Moduluebersicht(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Moduluebersicht")

        self.logger.info("📌 Modulübersicht geladen.")
        self.daten = self.master.logik.get_moduluebersicht_ansicht_daten()

        ttk.Label(self, text="📚 Modulübersicht", font=("Arial", 16)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Semester", "Modulname", "Kürzel", "Status", "ECTS", "Prüfungsform", "Startdatum"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Semester", text="Semester")
        self.tree.heading("Modulname", text="Modulname")
        self.tree.heading("Kürzel", text="Kürzel")
        self.tree.heading("Status", text="Status")
        self.tree.heading("ECTS", text="ECTS")
        self.tree.heading("Prüfungsform", text="Prüfungsform")
        self.tree.heading("Startdatum", text="Startdatum")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        for eintrag in self.daten:
            self.tree.insert("", tk.END, values=eintrag)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="➕ Modul hinzufügen", command=self.modul_hinzufuegen_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Modul bearbeiten", command=self.modul_bearbeiten_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Modul löschen", command=self.modul_loeschen).pack(side=tk.LEFT, padx=5)

    def modul_hinzufuegen_popup(self):
        """Popup-Fenster für das Hinzufügen eines neuen Moduls."""
        self.logger.info("📌 Öffne Modul-Hinzufügen-Dialog.")
        self.modul_popup("Neues Modul hinzufügen", "INSERT")

    def modul_bearbeiten_popup(self):
        """Popup-Fenster für das Bearbeiten eines bestehenden Moduls."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Fehler", "Bitte ein Modul auswählen.")
            return

        values = self.tree.item(selected_item, "values")
        self.logger.info(f"✏️ Öffne Modul-Bearbeiten-Dialog für ID {values[0]}")
        self.modul_popup("Modul bearbeiten", "UPDATE", values)

    def modul_popup(self, titel, aktion, modulwerte=None):
        """Popup-Fenster für Modul-Formular (Hinzufügen & Bearbeiten)."""
        popup = tk.Toplevel(self)
        popup.title(titel)
        popup.geometry("400x600")

        ttk.Label(popup, text="Semester-ID:").pack(pady=5)
        semester_combobox = ttk.Combobox(popup, values=[str(i) for i in range(1, 13)], state="readonly")
        semester_combobox.pack(pady=5)
        
        ttk.Label(popup, text="Modulname:").pack(pady=5)
        modulname_entry = ttk.Entry(popup)
        modulname_entry.pack(pady=5)

        ttk.Label(popup, text="Kürzel:").pack(pady=5)
        kuerzel_entry = ttk.Entry(popup)
        kuerzel_entry.pack(pady=5)

        ttk.Label(popup, text="Status:").pack(pady=5)
        status_combobox = ttk.Combobox(popup, values=["Offen", "In Bearbeitung", "Abgeschlossen"])
        status_combobox.pack(pady=5)

        ttk.Label(popup, text="Prüfungsform:").pack(pady=5)
        pruefungsform_combobox = ttk.Combobox(popup, values=["Klausur", "Portfolio", "Fachpräsentation"])
        pruefungsform_combobox.pack(pady=5)

        ttk.Label(popup, text="ECTS-Punkte:").pack(pady=5)
        ects_combobox = ttk.Combobox(popup, values=["5", "10"], state="readonly")
        ects_combobox.pack(pady=5)

        ttk.Label(popup, text="Note (1.0 - 5.0, optional):").pack(pady=5)
        note_entry = ttk.Entry(popup)
        note_entry.pack(pady=5)

        ttk.Label(popup, text="Startdatum auswählen:").pack(pady=5)
        kalender = Calendar(popup, selectmode="day", date_pattern="yyyy-mm-dd")
        kalender.pack(pady=5)

        if modulwerte:
            semester_combobox.set(str(modulwerte[1]))
            modulname_entry.insert(0, modulwerte[2])
            kuerzel_entry.insert(0, modulwerte[3])
            status_combobox.set(modulwerte[4])
            pruefungsform_combobox.set(modulwerte[6])
            ects_combobox.set(str(modulwerte[5]))
            note_entry.insert(0, modulwerte[7] if modulwerte[7] else "")
            kalender.set_date(modulwerte[8])

        ttk.Button(popup, text="💾 Speichern", command=lambda: self.modul_speichern(
            popup, aktion, modulwerte[0] if modulwerte else None, semester_combobox.get(), modulname_entry.get(),
            kuerzel_entry.get(), status_combobox.get(), pruefungsform_combobox.get(),
            ects_combobox.get(), note_entry.get(), kalender.get_date()
        )).pack(pady=10)

    def modul_speichern(self, popup, aktion, modul_id, semester_id, modulname, kuerzel, status, pruefungsform, ects, note, startdatum):
        """Speichert das Modul in die Datenbank (Neu oder Update)."""
        self.logger.info(f"✏️ {aktion} Modul: {modulname}, {kuerzel}")

        if not semester_id or not modulname or not kuerzel or not status or not pruefungsform or not ects or not startdatum:
            self.logger.error("❌ Fehler: Nicht alle Pflichtfelder ausgefüllt.")
            messagebox.showerror("Fehler", "Bitte alle Pflichtfelder ausfüllen!")
            return

        try:
            semester_id = int(semester_id)
            if semester_id < 1 or semester_id > 12:
                raise ValueError
        except ValueError:
            self.logger.error("❌ Fehler: Ungültige Semester-ID.")
            messagebox.showerror("Fehler", "Semester-ID muss eine Zahl zwischen 1 und 12 sein.")
            return

        try:
            ects = int(ects)
        except ValueError:
            self.logger.error("❌ Fehler: Ungültige ECTS-Punkte.")
            messagebox.showerror("Fehler", "Bitte wählen Sie 5 oder 10 ECTS-Punkte aus.")
            return

        try:
            note = float(note) if note else None
            if note and (note < 1.0 or note > 5.0):
                raise ValueError
        except ValueError:
            self.logger.error("❌ Fehler: Ungültige Note.")
            messagebox.showerror("Fehler", "Die Note muss zwischen 1.0 und 5.0 liegen.")
            return

        daten = (semester_id, modulname, kuerzel, status, pruefungsform, note, ects, startdatum) if aktion == "INSERT" else (modul_id, semester_id, modulname, kuerzel, status, pruefungsform, note, ects, startdatum)
        erfolg = self.master.logik.set_moduluebersicht_ansicht_daten(aktion, daten)

        if erfolg:
            self.logger.info(f"✅ Modul erfolgreich gespeichert: {daten}")
            messagebox.showinfo("Erfolg", f"Modul erfolgreich {aktion.lower()}!")
            popup.destroy()
            self.tree.delete(*self.tree.get_children())
            for eintrag in self.master.logik.get_moduluebersicht_ansicht_daten():
                self.tree.insert("", tk.END, values=eintrag)
        else:
            self.logger.error("❌ Fehler beim Speichern des Moduls.")
            messagebox.showerror("Fehler", "Modul konnte nicht gespeichert werden.")

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