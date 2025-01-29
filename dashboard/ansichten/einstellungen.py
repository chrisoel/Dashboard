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
        daten = self.master.logik.get_einstellungen_ansicht_daten()

        ttk.Label(self, text="⚙️ Einstellungen", font=("Arial", 16)).pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack(pady=10)

        ttk.Label(frame, text="📚 Studiengang:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.studiengang_entry = ttk.Entry(frame)
        self.studiengang_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="📅 Startdatum:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.kalender = Calendar(frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.kalender.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="🏖️ Urlaubssemester:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.urlaub_var1 = tk.IntVar()
        self.urlaub_var2 = tk.IntVar()
        ttk.Checkbutton(frame, text="Urlaubssemester 1", variable=self.urlaub_var1).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(frame, text="Urlaubssemester 2", variable=self.urlaub_var2).grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="📆 Arbeitstage:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.arbeitstage_vars = {
            "MO": tk.IntVar(),
            "DI": tk.IntVar(),
            "MI": tk.IntVar(),
            "DO": tk.IntVar(),
            "FR": tk.IntVar(),
            "SA": tk.IntVar(),
            "SO": tk.IntVar(),
        }
        workdays_frame = ttk.Frame(frame)
        workdays_frame.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        for i, (tag, var) in enumerate(self.arbeitstage_vars.items()):
            ttk.Checkbutton(workdays_frame, text=tag, variable=var).grid(row=0, column=i, sticky="w")

        ttk.Label(frame, text="⏳ Zeitmodell:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.zeitmodell_combobox = ttk.Combobox(frame, values=["Vollzeit", "Teilzeit I", "Teilzeit II"])
        self.zeitmodell_combobox.grid(row=5, column=1, padx=5, pady=5)
        self.zeitmodell_combobox.current(0)

        if daten:
            self.studiengang_entry.insert(0, daten[0][0])
            self.kalender.selection_set(daten[0][1])
            urlaubssemester = daten[0][2] if len(daten[0]) > 2 else 0
            if urlaubssemester >= 1:
                self.urlaub_var1.set(1)
            if urlaubssemester == 2:
                self.urlaub_var2.set(1)
            arbeitstage = daten[0][3].split("_") if len(daten[0]) > 3 and daten[0][3] else []
            for tag in arbeitstage:
                if tag in self.arbeitstage_vars:
                    self.arbeitstage_vars[tag].set(1)
            self.zeitmodell_combobox.set(daten[0][4] if len(daten[0]) > 4 else "Vollzeit")

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="💾 Änderungen speichern", command=self.speichern).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Alle Daten löschen", command=self.datenbank_loeschen).pack(side=tk.LEFT, padx=5)

    def speichern(self):
        """Speichert die geänderten Einstellungen in die Datenbank."""
        neuer_studiengang = self.studiengang_entry.get().strip()
        neues_datum = self.kalender.get_date()
        urlaubssemester = self.urlaub_var1.get() + self.urlaub_var2.get()
        arbeitstage = "_".join([tag for tag, var in self.arbeitstage_vars.items() if var.get()])
        neues_zeitmodell = self.zeitmodell_combobox.get()

        if not neuer_studiengang:
            messagebox.showerror("Fehler", "Bitte einen Studiengang eingeben.")
            return

        daten = (neuer_studiengang, neues_datum, urlaubssemester, arbeitstage, neues_zeitmodell)
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