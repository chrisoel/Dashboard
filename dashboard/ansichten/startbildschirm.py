import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from ansicht_enum import AnsichtTyp
import logging


class Startbildschirm(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Startbildschirm")

        self.zeitmodell_map = {
            "Vollzeit": "Vollzeit",
            "Teilzeit I": "TeilzeitI",
            "Teilzeit II": "TeilzeitII"
        }

        self.logger.info("📌 Startbildschirm geladen.")
        self.erstelle_gui()
        self.lade_daten()

    def erstelle_gui(self):
        """Erstellt die Grundstruktur des Startbildschirms."""
        ttk.Label(self, text="Willkommen im IU Dashboard!", font=("Arial", 16)).pack(pady=10)

    def lade_daten(self):
        """Lädt die Studiendaten und zeigt die passende Ansicht an."""
        daten = self.master.logik.get_startbildschirm_ansicht_daten()

        if not daten or not daten[0][1]:
            self.logger.warning("⚠️ Kein Studienstart hinterlegt. Nutzer muss Daten eingeben.")
            self.zeige_studienstart_eingabe()
        else:
            self.logger.info("✅ Studienstart bereits hinterlegt. Studiengang wird angezeigt.")
            self.zeige_studiengang(daten)

    def zeige_studiengang(self, daten):
        """Zeigt die vorhandenen Studiengangsdaten als Tabelle an."""
        tree = ttk.Treeview(self, columns=("Name", "Startdatum"), show="headings")
        tree.heading("Name", text="Studiengang")
        tree.heading("Startdatum", text="Startdatum")
        tree.pack(fill=tk.BOTH, expand=True)

        for eintrag in daten:
            tree.insert("", tk.END, values=eintrag)

    def zeige_studienstart_eingabe(self):
        """Zeigt das Eingabeformular für den Studienstart an."""
        frame = ttk.Frame(self)
        frame.pack(pady=20)

        ttk.Label(frame, text="📚 Bitte geben Sie Ihre Studieninformationen ein:").pack(pady=5)

        self.studiengang_entry = self.erstelle_eingabezeile(frame, "Studiengangsname:")
        self.kalender = self.erstelle_kalender(frame)
        self.urlaubssemester_vars = self.erstelle_urlaubssemester_optionen(frame)
        self.zeitmodell_var = self.erstelle_zeitmodell_dropdown(frame)

        ttk.Button(frame, text="💾 Speichern", command=self.speichere_studienstart).pack(pady=10)

    def erstelle_eingabezeile(self, frame, text):
        """Erstellt eine Eingabezeile mit Label."""
        ttk.Label(frame, text=text).pack()
        entry = ttk.Entry(frame)
        entry.pack(pady=5)
        return entry

    def erstelle_kalender(self, frame):
        """Erstellt ein Kalender-Widget zur Datumsauswahl."""
        ttk.Label(frame, text="Startdatum auswählen:").pack()
        kalender = Calendar(frame, selectmode="day", date_pattern="yyyy-mm-dd")
        kalender.pack(pady=5)
        return kalender

    def erstelle_urlaubssemester_optionen(self, frame):
        """Erstellt die Auswahloptionen für Urlaubssemester."""
        ttk.Label(frame, text="Urlaubssemester: (max. 2)").pack()
        vars_ = [tk.BooleanVar() for _ in range(2)]

        for i, var in enumerate(vars_):
            ttk.Checkbutton(frame, text=f"Urlaubssemester {i+1}", variable=var, command=self.update_urlaubssemester).pack(pady=2)

        return vars_

    def erstelle_zeitmodell_dropdown(self, frame):
        """Erstellt das Dropdown-Menü zur Auswahl des Zeitmodells."""
        ttk.Label(frame, text="Zeitmodell auswählen:").pack(pady=5)
        zeitmodell_var = tk.StringVar()
        dropdown = ttk.Combobox(frame, textvariable=zeitmodell_var, state="readonly")
        dropdown["values"] = tuple(self.zeitmodell_map.keys())
        dropdown.pack(pady=5)
        return zeitmodell_var

    def update_urlaubssemester(self):
        """Stellt sicher, dass maximal 2 Urlaubssemester ausgewählt werden können."""
        aktive = [var for var in self.urlaubssemester_vars if var.get()]
        if len(aktive) > 2:
            self.logger.warning("⚠️ Mehr als 2 Urlaubssemester gewählt, deaktiviere zuletzt aktivierten.")
            for var in reversed(self.urlaubssemester_vars):
                if var.get():
                    var.set(False)
                    break

    def speichere_studienstart(self):
        """Speichert die eingegebenen Studiendaten und überprüft die Eingaben."""
        studiengang = self.studiengang_entry.get().strip()
        datum_text = self.kalender.get_date()
        zeitmodell = self.zeitmodell_var.get()

        if not self.validiere_eingaben(studiengang, zeitmodell, datum_text):
            return

        urlaubssemester = sum(var.get() for var in self.urlaubssemester_vars)
        daten = (studiengang, datum_text, urlaubssemester, self.zeitmodell_map[zeitmodell])

        erfolgreich = self.master.logik.set_startbildschirm_ansicht_daten(daten)

        if erfolgreich:
            self.logger.info(f"✅ Studienstart erfolgreich gespeichert: {daten}")
            messagebox.showinfo("Gespeichert", "Ihr Studienstart wurde erfolgreich hinterlegt.")
            self.master.ansicht_wechseln(AnsichtTyp.MODULUEBERSICHT)
        else:
            self.logger.error("❌ Fehler beim Speichern des Studienstarts.")
            messagebox.showerror("Fehler", "Es gab ein Problem beim Speichern der Daten. Bitte erneut versuchen.")

    def validiere_eingaben(self, studiengang, zeitmodell, datum_text):
        """Überprüft die Benutzereingaben auf Fehler."""
        if not studiengang:
            self.logger.error("❌ Fehler: Kein Studiengang eingegeben.")
            messagebox.showerror("Fehler", "Bitte geben Sie einen Studiengangsnamen ein.")
            return False

        if not zeitmodell:
            self.logger.error("❌ Fehler: Kein Zeitmodell ausgewählt.")
            messagebox.showerror("Fehler", "Bitte wählen Sie ein Zeitmodell aus.")
            return False

        try:
            datetime.strptime(datum_text, "%Y-%m-%d")
        except ValueError:
            self.logger.error("❌ Fehler: Ungültiges Datum eingegeben.")
            messagebox.showerror("Fehler", "Ungültiges Datum. Bitte erneut auswählen.")
            return False

        return True