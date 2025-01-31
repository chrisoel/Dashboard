import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from ansicht_enum import AnsichtTyp
from ansichten.startbildschirm import Startbildschirm
from ansichten.moduluebersicht import Moduluebersicht
from ansichten.studienfortschritt import Studienfortschritt
from ansichten.zeitmanagement import Zeitmanagement
from ansichten.einstellungen import Einstellungen
from logik import Logik
import logging


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IU Dashboard")
        self.geometry("800x600")

        self.logger = logging.getLogger("Dashboard")
        self.logik = Logik()
        self.logik.starten()

        self.navigation = None
        self.inhalt = None
        self.aktuelle_ansicht = None

        self.ansicht_typen = {
            AnsichtTyp.MODULUEBERSICHT: Moduluebersicht,
            AnsichtTyp.STUDIENFORTSCHRITT: Studienfortschritt,
            AnsichtTyp.ZEITMANAGEMENT: Zeitmanagement,
            AnsichtTyp.EINSTELLUNGEN: Einstellungen,
        }

        self.logger.info("🚀 Dashboard gestartet, prüfe Studienstart...")
        self.studienstart_pruefen()

    def navigation_erstellen(self):
        """Erstellt die Navigationsleiste (ohne den Startbildschirm)."""
        if self.navigation:
            return 

        self.navigation = ttk.Frame(self, width=200)
        self.navigation.pack(side=tk.LEFT, fill=tk.Y)

        for ansicht in self.ansicht_typen:
            button = ttk.Button(
                self.navigation,
                text=ansicht.value,
                command=lambda ansicht=ansicht: self.ansicht_wechseln(ansicht)
            )
            button.pack(fill=tk.X)

        self.logger.info("🧭 Navigationsleiste erstellt (ohne Startbildschirm).")

    def studienstart_pruefen(self):
        """Prüft, ob ein Studienstartdatum hinterlegt ist, und zwingt ggf. eine Eingabe."""
        daten = self.logik.get_startbildschirm_ansicht_daten()

        if not daten or not daten[0][1]:
            self.logger.warning("⚠️ Kein Studienstart hinterlegt. Starte Startbildschirm...")
            self.ansicht_wechseln(AnsichtTyp.STARTBILDSCHIRM)
        else:
            self.logger.info("✅ Studienstart vorhanden. Starte mit Modulübersicht...")
            self.navigation_erstellen()
            self.ansicht_wechseln(AnsichtTyp.MODULUEBERSICHT)

    def ansicht_wechseln(self, ansicht: AnsichtTyp):
        """Wechselt die Ansicht und zeigt Navigation nach Studienstart an."""
        if self.aktuelle_ansicht:
            self.aktuelle_ansicht.pack_forget()

        if ansicht == AnsichtTyp.MODULUEBERSICHT and not self.navigation:
            self.logger.info("🔄 Wechsel zur Modulübersicht -> Navigationsleiste aktivieren.")
            self.navigation_erstellen()

        ansicht_klasse = self.ansicht_typen.get(ansicht, Startbildschirm)
        self.aktuelle_ansicht = ansicht_klasse(self)
        self.aktuelle_ansicht.pack(fill=tk.BOTH, expand=True)

        self.logger.info(f"🔄 Wechsel zur Ansicht: {ansicht.value}")

    def beenden(self):
        """Beendet die Anwendung und trennt die Datenbankverbindung."""
        self.logger.info("⏹️ Dashboard wird beendet...")
        self.logik.beenden()
        self.destroy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = Dashboard()
    app.mainloop()