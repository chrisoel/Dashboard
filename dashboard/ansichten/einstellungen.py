import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import logging


class Einstellungen(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Einstellungen")
        
        self.logger.info("📌 Einstellungen geladen.")
        
        self.daten = self.master.logik.get_einstellungen_ansicht_daten()

        self.erstelle_gui()
        self.update_idletasks()
        self.lade_daten()

    def erstelle_gui(self):
        """Erstellt das GUI-Layout für die Einstellungen."""
        ttk.Label(self, text="⚙️ Einstellungen", font=("Arial", 16)).pack(pady=10)

        self.frame = ttk.Frame(self)
        self.frame.pack(pady=10)

        self.studiengang_entry = self.erzeuge_textfeld("📚 Studiengang:", 0)
        self.kalender = self.erzeuge_kalender("📅 Startdatum:", 1)

        self.urlaub_var1 = tk.IntVar()
        self.urlaub_var2 = tk.IntVar()
        self.erzeuge_checkbuttons("🏖️ Urlaubssemester:", 2, self.urlaub_var1, self.urlaub_var2)

        self.zeitmodell_var = tk.StringVar()
        self.zeitmodell_combobox = self.erzeuge_dropdown("⏳ Zeitmodell:", 4, ["Vollzeit", "Teilzeit I", "Teilzeit II"], self.zeitmodell_var)

        self.erzeuge_buttons()

    def erzeuge_textfeld(self, label_text, row):
        """Erzeugt ein Label mit einem Eingabefeld."""
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(self.frame)
        entry.grid(row=row, column=1, padx=5, pady=5)
        return entry

    def erzeuge_kalender(self, label_text, row):
        """Erzeugt ein Label mit einem Kalender-Widget."""
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        kalender = Calendar(self.frame, selectmode="day", date_pattern="yyyy-mm-dd")
        kalender.grid(row=row, column=1, padx=5, pady=5)
        return kalender

    def erzeuge_checkbuttons(self, label_text, row, var1, var2):
        """Erzeugt ein Label mit zwei Checkboxen für Urlaubssemester."""
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(self.frame, text="Urlaubssemester 1", variable=var1).grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(self.frame, text="Urlaubssemester 2", variable=var2).grid(row=row + 1, column=1, sticky="w")

    def erzeuge_dropdown(self, label_text, row, values, variable):
        """Erzeugt ein Label mit einer Dropdown-Combobox."""
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        combobox = ttk.Combobox(self.frame, textvariable=variable, values=values, state="readonly")
        combobox.grid(row=row, column=1, padx=5, pady=5)
        combobox.current(0)
        return combobox

    def erzeuge_buttons(self):
        """Erzeugt die Speicher- und Lösch-Buttons."""
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="💾 Änderungen speichern", command=self.speichern).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Alle Daten löschen", command=self.datenbank_loeschen).pack(side=tk.LEFT, padx=5)

    def lade_daten(self):
        """Lädt gespeicherte Benutzerdaten in die GUI."""
        if not self.daten:
            return

        self.studiengang_entry.insert(0, self.daten[0][0])
        self.kalender.selection_set(self.daten[0][1])

        urlaubssemester = self.daten[0][2] if len(self.daten[0]) > 2 else 0
        self.urlaub_var1.set(1 if urlaubssemester >= 1 else 0)
        self.urlaub_var2.set(1 if urlaubssemester == 2 else 0)

        zeitmodell_db = self.daten[0][3] if len(self.daten[0]) > 3 else "Vollzeit"
        self.zeitmodell_combobox.set(self.map_zeitmodell(zeitmodell_db, to_display=True))

    def speichern(self):
        """Speichert die geänderten Einstellungen in die Datenbank."""
        neuer_studiengang = self.studiengang_entry.get().strip()
        neues_datum = self.kalender.get_date()
        urlaubssemester = self.urlaub_var1.get() + self.urlaub_var2.get()
        neues_zeitmodell = self.map_zeitmodell(self.zeitmodell_var.get())

        if not neuer_studiengang:
            messagebox.showerror("Fehler", "Bitte einen Studiengang eingeben.")
            return

        daten = (neuer_studiengang, neues_datum, urlaubssemester, neues_zeitmodell)
        erfolg = self.master.logik.set_einstellungen_ansicht_daten("UPDATE", daten)

        if erfolg:
            self.logger.info(f"✅ Änderungen gespeichert: {daten}")
            messagebox.showinfo("Erfolg", "Änderungen erfolgreich gespeichert.")
        else:
            self.logger.error("❌ Fehler beim Speichern der Änderungen.")
            messagebox.showerror("Fehler", "Änderungen konnten nicht gespeichert werden.")

    def datenbank_loeschen(self):
        """Löscht die gesamte Datenbank und beendet die Anwendung."""
        bestätigung = messagebox.askyesno("Bestätigung", "Möchten Sie wirklich alle Daten löschen?\nDies kann nicht rückgängig gemacht werden!")
        if not bestätigung:
            return

        self.logger.warning("⚠️ Datenbank wird gelöscht...")
        erfolg = self.master.logik.set_einstellungen_ansicht_daten("DELETE")

        if erfolg:
            self.logger.info("✅ Datenbank gelöscht. Anwendung wird beendet.")
            messagebox.showinfo("Erfolg", "Datenbank gelöscht. Die Anwendung wird jetzt geschlossen.")
            self.master.beenden()
        else:
            self.logger.error("❌ Fehler beim Löschen der Datenbank.")
            messagebox.showerror("Fehler", "Datenbank konnte nicht gelöscht werden.")

    @staticmethod
    def map_zeitmodell(zeitmodell, to_display=False):
        """Übersetzt das Zeitmodell zwischen Datenbank- und GUI-Darstellung."""
        mapping = {
            "Vollzeit": "Vollzeit",
            "TeilzeitI": "Teilzeit I",
            "TeilzeitII": "Teilzeit II"
        }
        if to_display:
            return mapping.get(zeitmodell, "Vollzeit")
        return {v: k for k, v in mapping.items()}.get(zeitmodell, "Vollzeit")