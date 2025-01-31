import logging
from datenbank_zugriff import DatenbankZugriff

class Logik:
    def __init__(self):
        self.logger = logging.getLogger("Logik")
        self.datenbank = DatenbankZugriff()
    
    def starten(self) -> bool:
        """Startet die Logik-Schicht und verbindet zur Datenbank."""
        self.logger.info("🚀 Starte Logik-Schicht...")
        try:
            erfolgreich = self.datenbank.starten()
            if erfolgreich:
                self.logger.info("✅ Logik-Schicht erfolgreich gestartet.")
            else:
                self.logger.error("❌ Fehler beim Start der Logik-Schicht.")
            return erfolgreich
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten: {e}")
            return False
    
    def beenden(self) -> None:
        """Beendet die Logik-Schicht und trennt die Verbindung zur Datenbank."""
        self.logger.info("⏹️ Beende Logik-Schicht...")
        self.datenbank.trennen()
        self.logger.info("✅ Logik-Schicht erfolgreich beendet.")
    
    def get_daten_ansicht(self, ansicht_name: str):
        """Holt Daten für eine bestimmte Ansicht."""
        sql = f"SELECT * FROM {ansicht_name};"
        try:
            self.logger.info(f"🔍 Abrufe Daten für Ansicht '{ansicht_name}'...")
            ergebnisse = self.datenbank.abfragen(sql)
            self.logger.info(f"✅ Daten erfolgreich geladen: {len(ergebnisse)} Einträge.")
            return ergebnisse
        except Exception as e:
            self.logger.error(f"❌ Fehler bei '{ansicht_name}': {e}")
            return []
    
    def get_moduluebersicht_ansicht_daten(self):
        return self.get_daten_ansicht("moduluebersicht")

    def set_moduluebersicht_ansicht_daten(self, aktion: str, daten: tuple) -> bool:
        """Bearbeitet Moduleinträge (INSERT, UPDATE, DELETE)."""
        try:
            if aktion.upper() == "INSERT":
                self.logger.info(f"➕ Neues Modul wird eingefügt: {daten}")
                erfolg = self.datenbank.modul_speichern(*daten)

            elif aktion.upper() == "UPDATE":
                self.logger.info(f"✏️ Modul wird aktualisiert: {daten}")
                erfolg = self.datenbank.modul_aktualisieren(*daten)

            elif aktion.upper() == "DELETE":
                self.logger.info(f"🗑️ Modul wird gelöscht: ID {daten[0]}")
                erfolg = self.datenbank.modul_loeschen(daten[0])

            else:
                self.logger.error(f"❌ Ungültige Aktion '{aktion}' für Modulbearbeitung.")
                return False

            if erfolg:
                self.logger.info(f"✅ Aktion '{aktion}' erfolgreich durchgeführt.")
            else:
                self.logger.warning(f"⚠️ Aktion '{aktion}' war nicht erfolgreich.")

            return erfolg

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Modulbearbeitung ({aktion}): {e}")
            return False

    def get_startbildschirm_ansicht_daten(self):
        return self.get_daten_ansicht("startbildschirm")
    
    def set_startbildschirm_ansicht_daten(self, daten: tuple) -> bool:
        """Speichert die Studiengangsdaten ohne Arbeitstage."""
        if len(daten) != 4:
            self.logger.error("❌ Ungültige Anzahl an Parametern für den Studiengang.")
            return False

        self.logger.info(f"✏️ Speichern des Studiengangs: {daten}")
        return self.datenbank.studiengang_speichern(*daten)
    
    def get_studienfortschritt_ansicht_daten(self):
        return self.get_daten_ansicht("studienfortschritt")
    
    def get_zeitmanagement_ansicht_daten(self):
        return self.get_daten_ansicht("zeitmanagement")
    
    def get_einstellungen_ansicht_daten(self):
        return self.get_daten_ansicht("einstellungen")
    
    def set_einstellungen_ansicht_daten(self, aktion: str, daten: tuple = None) -> bool:
        """Setzt oder löscht die Einstellungen in der Datenbank."""
        return self.datenbank.einstellungen_verwalten(aktion, daten)