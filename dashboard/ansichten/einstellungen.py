"""
@file einstellungen.py
@brief Modul zur Verwaltung der Anwendungseinstellungen.

Dieses Modul stellt eine grafische Benutzeroberfläche für die Verwaltung von Einstellungen bereit.
Der Benutzer kann seinen Studiengang, das Startdatum, Urlaubssemester und das Zeitmodell ändern 
und speichern. Zudem besteht die Möglichkeit, die gesamte Datenbank zu löschen.

Die Daten werden in der Datenbank gespeichert und bei jedem Start der Anwendung geladen.

@author CHOE
@date 2025-01-31
@version 1.0
"""


import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import logging


class Einstellungen(ttk.Frame):
    """
    @brief GUI-Komponente für die Anwendungseinstellungen.

    Diese Klasse ermöglicht das Ändern und Speichern von Studiendaten wie Studiengangsname,
    Startdatum, Urlaubssemester und Zeitmodell. Zudem kann die gesamte Datenbank gelöscht werden.

    @extends ttk.Frame
    """

    def __init__(self, master):
        """
        @brief Initialisiert das Einstellungen-Widget.

        Erstellt die grafische Oberfläche und lädt die gespeicherten Einstellungen aus der Datenbank.

        @param master Das Hauptfenster (tkinter Parent Widget).
        """
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger("Einstellungen")
        
        self.zeitmodell_map = {
            "Vollzeit": "Vollzeit",
            "Teilzeit I": "TeilzeitI",
            "Teilzeit II": "TeilzeitII"
        }

        self.logger.info("📌 Einstellungen geladen.")
        
        self.daten = self.master.logik.get_einstellungen_ansicht_daten()

        self.erstelle_gui()
        self.update_idletasks()
        self.lade_daten()

    def erstelle_gui(self):
            """
            @brief Erstellt das GUI-Layout für die Einstellungen.

            Fügt Eingabefelder für den Studiengang, Startdatum, Urlaubssemester und das Zeitmodell hinzu.
            Zudem werden Buttons zum Speichern und Löschen der Datenbank erstellt.
            """
            ttk.Label(self, text="⚙️ Einstellungen", font=("Arial", 16)).pack(pady=10)

            self.frame = ttk.Frame(self)
            self.frame.pack(pady=10)

            self.studiengang_entry = self.erzeuge_textfeld("📚 Studiengang:", 0)
            self.kalender = self.erzeuge_kalender("📅 Startdatum:", 1)

            self.urlaub_var1 = tk.IntVar()
            self.urlaub_var2 = tk.IntVar()
            self.erzeuge_checkbuttons("🏖️ Urlaubssemester:", 2, self.urlaub_var1, self.urlaub_var2)

            self.zeitmodell_var = tk.StringVar()
            self.zeitmodell_combobox = self.erzeuge_dropdown("⏳ Zeitmodell:", 4, list(self.zeitmodell_map.keys()), self.zeitmodell_var)

            self.erzeuge_buttons()

    def erzeuge_textfeld(self, label_text, row):
        """
        @brief Erzeugt ein Label mit einem Eingabefeld.

        @param label_text Der anzuzeigende Label-Text.
        @param row Die Zeile in der GUI, in der das Element platziert wird.
        @return Ein Entry-Widget zur Texteingabe.
        """
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(self.frame)
        entry.grid(row=row, column=1, padx=5, pady=5)
        return entry

    def erzeuge_kalender(self, label_text, row):
        """
        @brief Erzeugt ein Label mit einem Kalender-Widget zur Datumsauswahl.

        @param label_text Der anzuzeigende Label-Text.
        @param row Die Zeile in der GUI, in der das Element platziert wird.
        @return Ein Calendar-Widget zur Datumsauswahl.
        """
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        kalender = Calendar(self.frame, selectmode="day", date_pattern="yyyy-mm-dd")
        kalender.grid(row=row, column=1, padx=5, pady=5)
        return kalender

    def erzeuge_checkbuttons(self, label_text, row, var1, var2):
        """
        @brief Erzeugt zwei Checkboxen zur Auswahl von Urlaubssemestern.

        @param label_text Der anzuzeigende Label-Text.
        @param row Die Zeile in der GUI, in der die Elemente platziert werden.
        @param var1 Boolean-Variable für die erste Checkbox.
        @param var2 Boolean-Variable für die zweite Checkbox.
        """
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(self.frame, text="Urlaubssemester 1", variable=var1).grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(self.frame, text="Urlaubssemester 2", variable=var2).grid(row=row + 1, column=1, sticky="w")

    def erzeuge_dropdown(self, label_text, row, values, variable):
        """
        @brief Erzeugt ein Dropdown-Menü für die Auswahl eines Wertes.

        @param label_text Der anzuzeigende Label-Text.
        @param row Die Zeile in der GUI, in der das Element platziert wird.
        @param values Eine Liste von Werten für das Dropdown-Menü.
        @param variable Die Variable, die das ausgewählte Element speichert.
        @return Ein Combobox-Widget für die Auswahl.
        """
        ttk.Label(self.frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        combobox = ttk.Combobox(self.frame, textvariable=variable, values=values, state="readonly")
        combobox.grid(row=row, column=1, padx=5, pady=5)
        combobox.current(0)
        return combobox
    
    def get_gui_zeitmodell(self, db_value):
        """
        @brief Konvertiert das Zeitmodell aus der Datenbank in eine GUI-lesbare Form.

        @param db_value Der in der Datenbank gespeicherte Wert.
        @return Die GUI-Darstellung des Zeitmodells.
        """
        return {v: k for k, v in self.zeitmodell_map.items()}.get(db_value, "Vollzeit")
    
    def get_db_zeitmodell(self, gui_value):
        """
        @brief Konvertiert das Zeitmodell aus der GUI in die Datenbank-Darstellung.

        @param gui_value Der vom Benutzer ausgewählte Wert.
        @return Die Datenbank-Darstellung des Zeitmodells.
        """
        return self.zeitmodell_map.get(gui_value, "Vollzeit")

    def erzeuge_buttons(self):
        """
        @brief Erstellt die Steuerungsbuttons für die Einstellungen.

        Diese Methode erzeugt die Buttons zur Steuerung der Einstellungen, 
        einschließlich eines Speicher-Buttons für Änderungen und eines Lösch-Buttons 
        für das Entfernen aller Daten.

        @details
        - Der Speicher-Button (`💾 Änderungen speichern`) ruft `self.speichern()` auf.
        - Der Lösch-Button (`🗑️ Alle Daten löschen`) ruft `self.datenbank_loeschen()` auf.
        - Die Buttons werden innerhalb eines Frames horizontal angeordnet.
        """
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="💾 Änderungen speichern", command=self.speichern).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Alle Daten löschen", command=self.datenbank_loeschen).pack(side=tk.LEFT, padx=5)

    def lade_daten(self):
        """
        @brief Lädt gespeicherte Benutzerdaten in die GUI.

        Diese Methode ruft die gespeicherten Einstellungen aus der Datenbank ab und 
        füllt die entsprechenden GUI-Elemente mit den gespeicherten Werten.

        @details
        - Falls keine gespeicherten Daten vorhanden sind, wird die Methode beendet.
        - Der Studiengang wird in das entsprechende Eingabefeld geladen.
        - Das Startdatum wird im Kalender-Widget gesetzt.
        - Die Urlaubssemester-Checkboxen werden basierend auf gespeicherten Werten aktualisiert.
        - Das Zeitmodell wird anhand der gespeicherten Daten in die GUI-Form konvertiert.

        @note Falls keine Daten in der Datenbank gespeichert sind, passiert nichts.
        """
        if not self.daten:
            return

        self.studiengang_entry.insert(0, self.daten[0][0])
        self.kalender.selection_set(self.daten[0][1])

        urlaubssemester = self.daten[0][2] if len(self.daten[0]) > 2 else 0
        self.urlaub_var1.set(1 if urlaubssemester >= 1 else 0)
        self.urlaub_var2.set(1 if urlaubssemester == 2 else 0)

        zeitmodell_db = self.daten[0][3] if len(self.daten[0]) > 3 else "Vollzeit"
        self.zeitmodell_combobox.set(self.get_gui_zeitmodell(zeitmodell_db))

    def speichern(self):
        """
        @brief Speichert die geänderten Einstellungen in die Datenbank.

        Überprüft die Benutzereingaben und speichert sie in der Datenbank. Falls erforderlich,
        wird eine Fehlermeldung angezeigt.
        """
        neuer_studiengang = self.studiengang_entry.get().strip()
        neues_datum = self.kalender.get_date()
        urlaubssemester = self.urlaub_var1.get() + self.urlaub_var2.get()
        neues_zeitmodell = self.get_db_zeitmodell(self.zeitmodell_var.get())

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
        """
        @brief Löscht die gesamte Datenbank und beendet die Anwendung.

        Diese Methode fragt den Benutzer, ob die gesamte Datenbank gelöscht werden soll.
        Falls der Benutzer bestätigt, wird der Löschvorgang ausgeführt und die Anwendung 
        nach erfolgreicher Löschung beendet.

        @note Dieser Vorgang kann nicht rückgängig gemacht werden!

        @exception sqlite3.Error Falls ein Fehler beim Löschen der Datenbank auftritt.
        """
        bestätigung = messagebox.askyesno(
            "Bestätigung", 
            "Möchten Sie wirklich alle Daten löschen?\nDies kann nicht rückgängig gemacht werden!"
        )
        
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