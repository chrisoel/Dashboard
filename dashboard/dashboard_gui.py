import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk
from ansicht_enum import AnsichtTyp
from ansichten.startbildschirm import Startbildschirm
from ansichten.moduluebersicht import Moduluebersicht
from ansichten.studienfortschritt import Studienfortschritt
from ansichten.zeitmanagement import Zeitmanagement
from ansichten.einstellungen import Einstellungen
from logik import Logik


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard")
        self.geometry("800x600")

        self.logik = Logik()
        self.logik.starten()

        self.navigation = None
        self.inhalt = None
        self.aktuelle_ansicht = None

        self.ansicht_typen = {
            AnsichtTyp.STARTBILDSCHIRM: Startbildschirm,
            AnsichtTyp.MODULUEBERSICHT: Moduluebersicht,
            AnsichtTyp.STUDIENFORTSCHRITT: Studienfortschritt,
            AnsichtTyp.ZEITMANAGEMENT: Zeitmanagement,
            AnsichtTyp.EINSTELLUNGEN: Einstellungen,
        }

        self.navigation_erstellen()
        self.ansicht_wechseln(AnsichtTyp.STARTBILDSCHIRM)

    def navigation_erstellen(self):
        """Erstellt die Navigationsleiste."""
        self.navigation = ttk.Frame(self, width=200)
        self.navigation.pack(side=tk.LEFT, fill=tk.Y)

        for ansicht in AnsichtTyp:
            button = ttk.Button(
                self.navigation,
                text=ansicht.value,
                command=lambda ansicht=ansicht: self.ansicht_wechseln(ansicht)
            )
            button.pack(fill=tk.X)

    def ansicht_wechseln(self, ansicht: AnsichtTyp):
        """Wechselt die Ansicht."""
        if self.aktuelle_ansicht:
            self.aktuelle_ansicht.pack_forget()

        ansicht_klasse = self.ansicht_typen[ansicht]
        self.aktuelle_ansicht = ansicht_klasse(self)
        self.aktuelle_ansicht.pack(fill=tk.BOTH, expand=True)

    def beenden(self):
        """Beendet die Anwendung und trennt die Datenbankverbindung."""
        self.logik.beenden()
        self.destroy()


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()