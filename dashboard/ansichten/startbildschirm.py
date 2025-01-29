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

        self.logger.info("📌 Startbildschirm geladen.")
        daten = self.master.logik.get_startbildschirm_ansicht_daten()

        ttk.Label(self, text="Willkommen im IU Dashboard!", font=("Arial", 16)).pack(pady=10)

        if not daten or not daten[0][1]:
            self.logger.warning("⚠️ Kein Studienstart hinterlegt. Nutzer muss Daten eingeben.")
            self.studienstart_eingeben()
        else:
            self.logger.info("✅ Studienstart bereits hinterlegt. Studiengang wird angezeigt.")
            self.studiengang_anzeigen(daten)

    def studiengang_anzeigen(self, daten):
        """Zeigt den Studiengang und das Startdatum an."""
        tree = ttk.Treeview(self, columns=("Name", "Startdatum"), show="headings")
        tree.heading("Name", text="Studiengang")
        tree.heading("Startdatum", text="Startdatum")
        tree.pack(fill=tk.BOTH, expand=True)

        for eintrag in daten:
            tree.insert("", tk.END, values=eintrag)

    def studienstart_eingeben(self):
        """Erzwingt die Eingabe des Studiengangs, Startdatums, Urlaubssemester, Arbeitstage und Zeitmodells."""
        frame = ttk.Frame(self)
        frame.pack(pady=20)

        ttk.Label(frame, text="📚 Bitte geben Sie Ihre Studieninformationen ein:").pack(pady=5)

        ttk.Label(frame, text="Studiengangsname:").pack()
        self.studiengang_entry = ttk.Entry(frame)
        self.studiengang_entry.pack(pady=5)

        ttk.Label(frame, text="Startdatum auswählen:").pack()
        self.kalender = Calendar(frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.kalender.pack(pady=5)

        ttk.Label(frame, text="Urlaubssemester: (max. 2)").pack()
        self.urlaubssemester_vars = [tk.BooleanVar() for _ in range(2)]
        self.urlaubssemester_buttons = []

        for i in range(2):
            btn = ttk.Checkbutton(frame, text=f"Urlaubssemester {i+1}", variable=self.urlaubssemester_vars[i], 
                                  command=self.update_urlaubssemester)
            btn.pack(pady=2)
            self.urlaubssemester_buttons.append(btn)

        ttk.Label(frame, text="Arbeitstage auswählen:").pack()
        self.arbeitstage_vars = {
            "MO": tk.BooleanVar(),
            "DI": tk.BooleanVar(),
            "MI": tk.BooleanVar(),
            "DO": tk.BooleanVar(),
            "FR": tk.BooleanVar(),
            "SA": tk.BooleanVar(),
            "SO": tk.BooleanVar()
        }
        self.arbeitstage_buttons = {}

        for tag, var in self.arbeitstage_vars.items():
            btn = ttk.Checkbutton(frame, text=tag, variable=var)
            btn.pack(side=tk.LEFT, padx=5)
            self.arbeitstage_buttons[tag] = btn

        ttk.Label(frame, text="Zeitmodell auswählen:").pack(pady=5)
        self.zeitmodell_var = tk.StringVar()
        self.zeitmodell_dropdown = ttk.Combobox(frame, textvariable=self.zeitmodell_var, state="readonly")
        self.zeitmodell_dropdown["values"] = ("Vollzeit", "Teilzeit I", "Teilzeit II")
        self.zeitmodell_dropdown.pack(pady=5)

        ttk.Button(frame, text="💾 Speichern", command=self.startdatum_speichern).pack(pady=10)

    def update_urlaubssemester(self):
        """Stellt sicher, dass maximal 2 Urlaubssemester aktiv sind."""
        aktive = [var for var in self.urlaubssemester_vars if var.get()]
        if len(aktive) > 2:
            self.logger.warning("⚠️ Mehr als 2 Urlaubssemester gewählt, deaktiviere zuletzt aktivierten.")
            for var in reversed(self.urlaubssemester_vars):
                if var.get():
                    var.set(False)
                    break

    def startdatum_speichern(self):
        """Speichert die Studieninformationen in die Datenbank."""
        studiengang = self.studiengang_entry.get().strip()
        datum_text = self.kalender.get_date()
        zeitmodell = self.zeitmodell_var.get()

        if not studiengang:
            self.logger.error("❌ Fehler: Kein Studiengang eingegeben.")
            messagebox.showerror("Fehler", "Bitte geben Sie einen Studiengangsnamen ein.")
            return

        if not zeitmodell:
            self.logger.error("❌ Fehler: Kein Zeitmodell ausgewählt.")
            messagebox.showerror("Fehler", "Bitte wählen Sie ein Zeitmodell aus.")
            return

        try:
            datum = datetime.strptime(datum_text, "%Y-%m-%d").date()
        except ValueError:
            self.logger.error("❌ Fehler: Ungültiges Datum eingegeben.")
            messagebox.showerror("Fehler", "Ungültiges Datum. Bitte erneut auswählen.")
            return

        urlaubssemester = sum(var.get() for var in self.urlaubssemester_vars)

        aktive_arbeitstage = [tag for tag, var in self.arbeitstage_vars.items() if var.get()]
        arbeitstage_sql = "_".join(aktive_arbeitstage)

        if not arbeitstage_sql:
            self.logger.error("❌ Fehler: Keine Arbeitstage ausgewählt.")
            messagebox.showerror("Fehler", "Bitte wählen Sie mindestens einen Arbeitstag aus.")
            return

        daten = (studiengang, datum_text, urlaubssemester, arbeitstage_sql, zeitmodell)
        erfolgreich = self.master.logik.set_startbildschirm_ansicht_daten(daten)

        if erfolgreich:
            self.logger.info(f"✅ Studienstart erfolgreich gespeichert: {daten}")
            messagebox.showinfo("Gespeichert", "Ihr Studienstart wurde erfolgreich hinterlegt.")
            self.master.ansicht_wechseln(AnsichtTyp.MODULUEBERSICHT)
        else:
            self.logger.error("❌ Fehler beim Speichern des Studienstarts.")
            messagebox.showerror("Fehler", "Es gab ein Problem beim Speichern der Daten. Bitte erneut versuchen.")